from datetime import datetime, time, timedelta
from typing import Optional
import pandas as pd
from core.config import AttendanceConfig

def format_hhmm_str(val, is_hours_float=False) -> str:
    """Convierte un valor numérico (horas flotantes o minutos enteros) a formato HH:MM (ej. 11:51, 00:15)."""
    if pd.isna(val) or val is None or val == "":
        return "00:00"
    val_str = str(val).strip()
    if ":" in val_str and len(val_str.split(":")) == 2:
        return val_str
    try:
        num = float(val)
        if num <= 0:
            return "00:00"
        total_min = int(round(num * 60.0)) if is_hours_float else int(round(num))
        h = total_min // 60
        m = total_min % 60
        return f"{h:02d}:{m:02d}"
    except Exception:
        return "00:00"

def time_to_seconds(t: time) -> int:
    if t is None:
        return 0
    return t.hour * 3600 + t.minute * 60 + t.second

def detectar_horario(hora_ref: time, is_salida_only: bool = False, config: AttendanceConfig = None) -> str:
    """
    Detecta si el horario corresponde a TURNO DÍA (04:00 - 16:00) o TURNO NOCHE (16:00 - 04:00).
    - Turno Día: Entrada entre las 04:00 AM y las 15:59 PM.
    - Turno Noche: Entrada a partir de las 16:00 PM (4:00 PM) o de madrugada (< 04:00 AM).
    """
    if hora_ref is None:
        return "DIA"
    
    h_sec = time_to_seconds(hora_ref)
    
    if is_salida_only:
        if 11 * 3600 <= h_sec <= 23 * 3600 + 59 * 60:
            return "DIA"
        else:
            return "NOCHE"
    else:
        if 4 * 3600 <= h_sec < 16 * 3600:
            return "DIA"
        else:
            return "NOCHE"

def calcular_tardanza(horario: str, hora_entrada: time, config: AttendanceConfig, es_media_jornada: bool = False) -> int:
    """
    Tardanza se calcula en minutos pasados los 15 minutos de tolerancia.
    Mapea correctamente las entradas de relevo (05:00, 17:00) y media jornada tarde (13:00).
    """
    if hora_entrada is None:
        return 0
    
    ent_sec = time_to_seconds(hora_entrada)

    # Evaluar horario programado de inicio según el rango de marcación real
    if 4 * 3600 <= ent_sec <= 6 * 3600: # Relevo 05:00 AM
        hora_prog = time(5, 0)
    elif 16 * 3600 <= ent_sec <= 18 * 3600: # Relevo 17:00 PM (Caso Manuel Bermeo 16:54 PM)
        hora_prog = time(17, 0)
    elif es_media_jornada and 11 * 3600 <= ent_sec <= 14 * 3600: # Media jornada tarde 13:00
        hora_prog = time(13, 0)
    else:
        hora_prog = time(7, 0) if horario == "DIA" else time(19, 0)

    prog_sec = time_to_seconds(hora_prog)
    limite_tolerancia_sec = prog_sec + (config.tolerancia_entrada_min * 60) # + 15 min
    
    if ent_sec <= limite_tolerancia_sec:
        return 0
    else:
        return int((ent_sec - limite_tolerancia_sec) // 60)


def calcular_salida_anticipada(horario: str, hora_salida: time, hora_entrada: time, config: AttendanceConfig) -> int:
    """
    Salida anticipada se calcula respecto a 19:00 (Turno Día) u 07:00 (Turno Noche).
    Solo si entró a las 05:00 AM o 17:00 PM (Relevo), la salida programada es 17:00 u 05:00.
    """
    if hora_salida is None:
        return 0
    
    sal_sec = time_to_seconds(hora_salida)
    ent_sec = time_to_seconds(hora_entrada) if hora_entrada else None

    if horario == "DIA":
        if ent_sec and 4 * 3600 + 30 * 60 <= ent_sec <= 5 * 3600 + 30 * 60:
            hora_prog_salida = time(17, 0)
        else:
            hora_prog_salida = time(19, 0)
    else: # NOCHE
        if ent_sec and 16 * 3600 + 30 * 60 <= ent_sec <= 17 * 3600 + 30 * 60:
            hora_prog_salida = time(5, 0)
        else:
            hora_prog_salida = time(7, 0)

    prog_salida_sec = time_to_seconds(hora_prog_salida)
    limite_tolerancia_salida_sec = prog_salida_sec - (config.tolerancia_salida_min * 60)
    
    if horario == "DIA":
        if sal_sec >= limite_tolerancia_salida_sec or sal_sec <= time_to_seconds(time(7, 0)):
            return 0
        else:
            return int((limite_tolerancia_salida_sec - sal_sec) // 60)
    else: # NOCHE
        if sal_sec >= limite_tolerancia_salida_sec:
            return 0
        else:
            return int((limite_tolerancia_salida_sec - sal_sec) // 60)


def calcular_exceso_jornada(horario: str, hora_salida: time, hora_entrada: time, config: AttendanceConfig) -> int:
    """
    Exceso de jornada en minutos al salir después de la hora programada de salida (19:00 o 07:00).
    """
    if hora_salida is None:
        return 0
        
    sal_sec = time_to_seconds(hora_salida)
    ent_sec = time_to_seconds(hora_entrada) if hora_entrada else None

    if horario == "DIA":
        if ent_sec and 4 * 3600 + 30 * 60 <= ent_sec <= 5 * 3600 + 30 * 60:
            hora_prog_salida = time(17, 0)
        else:
            hora_prog_salida = time(19, 0)

        prog_salida_sec = time_to_seconds(hora_prog_salida)
        if sal_sec >= prog_salida_sec:
            return int((sal_sec - prog_salida_sec) // 60)
        elif sal_sec <= time_to_seconds(time(7, 0)):
            return int(((86400 - prog_salida_sec) + sal_sec) // 60)
        return 0
    else: # TURNO NOCHE
        if ent_sec and 16 * 3600 + 30 * 60 <= ent_sec <= 17 * 3600 + 30 * 60:
            hora_prog_salida = time(5, 0)
        else:
            hora_prog_salida = time(7, 0)

        prog_salida_sec = time_to_seconds(hora_prog_salida)
        if sal_sec > prog_salida_sec:
            return int((sal_sec - prog_salida_sec) // 60)
        return 0

def calcular_estado_asistencia(tiene_entrada: bool, tiene_salida: bool, tardanza: int, salida_ant: int, incidencias: str, total_horas_adic_min: int) -> str:
    if not tiene_entrada and not tiene_salida:
        return "FALTA"
    if tiene_entrada and not tiene_salida:
        return "SALIDA PENDIENTE"
    if not tiene_entrada and tiene_salida:
        return "ENTRADA PENDIENTE"
    
    if incidencias and len(str(incidencias).strip()) > 0:
        return "ASISTIO CON INCIDENCIAS"
    if tardanza > 0 and salida_ant > 0:
        return "TARDANZA + SALIDA ANTICIPADA"
    if tardanza > 0:
        return "TARDANZA"
    if salida_ant > 0:
        return "SALIDA ANTICIPADA"
    if total_horas_adic_min > 0:
        return "ASISTIO CON H.E."
    
    return "ASISTIO"

def parse_time_val(val) -> Optional[time]:
    if pd.isna(val) or val is None or val == "":
        return None
    if isinstance(val, time):
        return val
    if isinstance(val, datetime):
        return val.time()
    val_str = str(val).strip()
    if ' ' in val_str:
        val_str = val_str.split(' ')[-1].strip()
    elif 'T' in val_str:
        val_str = val_str.split('T')[-1].strip()
        
    parts = val_str.split(':')
    if len(parts) >= 2:
        try:
            h = int(parts[0])
            m = int(parts[1])
            s = int(parts[2].split('.')[0]) if len(parts) > 2 else 0
            return time(h, m, s)
        except Exception:
            return None
    return None

def parse_date_val(val) -> Optional[str]:
    if pd.isna(val) or val is None or val == "":
        return None
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d')
    val_str = str(val).strip()
    try:
        dt = datetime.strptime(val_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    try:
        dt = datetime.strptime(val_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    try:
        dt = pd.to_datetime(val_str, dayfirst=True)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return val_str

def procesar_asistencia_df(df_trabajadores: pd.DataFrame, df_marcaciones: pd.DataFrame, df_horas_extra_in: pd.DataFrame = None, config: AttendanceConfig = None) -> tuple:
    if config is None:
        config = AttendanceConfig()
        
    if df_trabajadores.empty or 'DNI' not in df_trabajadores.columns:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

    # Limpieza de DNI
    df_trabajadores['DNI_STR'] = df_trabajadores['DNI'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    workers_dict = {}
    for _, tr in df_trabajadores.iterrows():
        d_str = str(tr['DNI_STR']).strip()
        d_clean = d_str.lstrip('0') or '0'
        tr_info = tr.to_dict()
        tr_info['OFFICIAL_DNI'] = d_str
        workers_dict[d_str] = tr_info
        workers_dict[d_clean] = tr_info
    
    if df_marcaciones.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
        
    df_marcaciones = df_marcaciones.copy()
    dni_col = 'ID' if 'ID' in df_marcaciones.columns else ('DNI' if 'DNI' in df_marcaciones.columns else df_marcaciones.columns[0])
    df_marcaciones['DNI_STR'] = df_marcaciones[dni_col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    
    date_col = 'Fecha' if 'Fecha' in df_marcaciones.columns else 'FECHA'
    df_marcaciones['Fecha_Clean'] = df_marcaciones[date_col].apply(parse_date_val)
    
    time_col = 'Tiempo' if 'Tiempo' in df_marcaciones.columns else ('Hora' if 'Hora' in df_marcaciones.columns else 'HORA')
    df_marcaciones['Hora_Clean'] = df_marcaciones[time_col].apply(parse_time_val)
    
    tipo_col = 'Tipo de pase de tarjeta' if 'Tipo de pase de tarjeta' in df_marcaciones.columns else 'TIPO'
    
    # Filtrado Punto 9: Eliminar filas vacías, de encabezados duplicados o sin hora válida
    df_marcaciones = df_marcaciones[
        df_marcaciones['DNI_STR'].notna() &
        df_marcaciones['Fecha_Clean'].notna() &
        df_marcaciones['Hora_Clean'].notna() &
        ~df_marcaciones['DNI_STR'].str.lower().str.contains('fecha:|semana:|periodo:|desconocido|none|nan', regex=True, na=False)
    ]
    if tipo_col in df_marcaciones.columns:
        df_marcaciones = df_marcaciones[
            ~df_marcaciones[tipo_col].astype(str).str.lower().str.contains('indefinid', regex=True, na=False)
        ]
    
    # Deduplicar marcaciones estrictamente idénticas
    df_marcaciones = df_marcaciones.drop_duplicates(
        subset=['DNI_STR', 'Fecha_Clean', 'Hora_Clean', tipo_col]
    )

    # Agrupar marcaciones por DNI y Fecha
    grouped = df_marcaciones.groupby(['DNI_STR', 'Fecha_Clean'])
    
    rows_asistencia = []
    rows_horas_extra = []
    rows_incidencias = []
    processed_keys = set()
    consumed_swipes = set()
    
    all_dates = [
        d for d in df_marcaciones['Fecha_Clean'].dropna().unique() 
        if d and isinstance(d, str) and len(d) == 10 and d[4] == '-' and d[7] == '-'
    ]
    all_dnis = [w for w in df_trabajadores['DNI_STR'].unique() if w and str(w).lower() != 'desconocido' and str(w).lower() != 'none']

    for (dni, fecha), group in grouped:
        if not fecha or not dni or len(fecha) != 10 or dni.lower() == 'desconocido' or 'fecha:' in dni.lower():
            continue
            
        dni_clean = str(dni).strip().lstrip('0') or '0'
        worker_info = workers_dict.get(dni) or workers_dict.get(dni_clean) or {
            'APELLIDOS': 'DESCONOCIDO',
            'NOMBRES': '',
            'CARGO': 'N/A',
            'AREA': 'N/A'
        }
        dni_export = worker_info.get('OFFICIAL_DNI', worker_info.get('DNI', dni))
        processed_keys.add((dni, fecha))
        processed_keys.add((dni_export, fecha))
        processed_keys.add((dni_clean, fecha))
        
        # Filtrar marcaciones ya consumidas en Turno NOCHE del día anterior
        valid_rows = group[
            ~group.apply(lambda r: (dni_clean, fecha, r['Hora_Clean'].strftime('%H:%M') if pd.notna(r['Hora_Clean']) else '') in consumed_swipes, axis=1)
        ].dropna(subset=['Hora_Clean']).sort_values('Hora_Clean')

        if valid_rows.empty:
            continue

        # SILENCIAR Y RECTIFICAR SILENCIOSAMENTE MARCACIONES ERRÓNEAS (PUNTOS 1 Y 6)
        # Caso Jhon Agreda (Punto 1): Marcación accidental de 'Inicio de horas extra' a las 07:03 a la par con 'Registro de entrada' a las 07:03.
        he_early_err = [
            r for _, r in valid_rows.iterrows()
            if ('inicio de horas extra' in str(r.get(tipo_col, '')).lower() or 'inicio h.e.' in str(r.get(tipo_col, '')).lower())
            and time_to_seconds(r['Hora_Clean']) < 43200 # Mañana
        ]
        ent_early = [
            r for _, r in valid_rows.iterrows()
            if 'entrada' in str(r.get(tipo_col, '')).lower() and not ('horas extra' in str(r.get(tipo_col, '')).lower() or 'he' in str(r.get(tipo_col, '')).lower())
            and time_to_seconds(r['Hora_Clean']) < 43200
        ]
        if he_early_err and ent_early:
            he_h = he_early_err[0]['Hora_Clean']
            ent_h = ent_early[0]['Hora_Clean']
            if abs(time_to_seconds(he_h) - time_to_seconds(ent_h)) <= 300: # < 5 min
                valid_rows = valid_rows[valid_rows['Hora_Clean'] != he_h]

        # Caso Yenkli Ordoñez / Doble marcación al retirarse en la tarde (Punto 6):
        # Entrada 06:41 AM, luego 19:01 Entrada y 19:01 Salida. Descartar la entrada errónea de las 19:01 silenciosamente sin poner mensaje de corrección.
        has_morning_entry = any(
            'entrada' in str(r.get(tipo_col, '')).lower() and time_to_seconds(r['Hora_Clean']) < 43200
            for _, r in valid_rows.iterrows()
        )
        if has_morning_entry:
            evening_swipes = [
                r for _, r in valid_rows.iterrows()
                if time_to_seconds(r['Hora_Clean']) >= 57600
            ]
            if len(evening_swipes) >= 2:
                evening_swipes.sort(key=lambda r: time_to_seconds(r['Hora_Clean']))
                first_ev = evening_swipes[0]
                second_ev = evening_swipes[1]
                t_diff = time_to_seconds(second_ev['Hora_Clean']) - time_to_seconds(first_ev['Hora_Clean'])
                if t_diff <= 300:
                    if 'entrada' in str(first_ev.get(tipo_col, '')).lower() and 'salida' in str(second_ev.get(tipo_col, '')).lower():
                        valid_rows = valid_rows[valid_rows['Hora_Clean'] != first_ev['Hora_Clean']]

        # Caso Error Humano en Biométrico (Turno Noche):
        # Si NO existe ninguna entrada previa en el día (antes de las 16:00 PM)
        # y el trabajador marca entre las 16:00 y las 21:00 PM etiquetada como 'salida' por error humano,
        # y al día siguiente existe salida en la mañana (<= 09:00 AM):
        # Reclasificar lógicamente la marcación de la tarde como ENTRADA para Turno Noche.
        no_prior_entry = not any(
            'entrada' in str(r.get(tipo_col, '')).lower() and time_to_seconds(r['Hora_Clean']) < 57600 # Antes de las 16:00 PM
            for _, r in valid_rows.iterrows()
        )
        if no_prior_entry:
            evening_swipes_salida = [
                idx_r for idx_r, r in valid_rows.iterrows()
                if 57600 <= time_to_seconds(r['Hora_Clean']) <= 75600 # 16:00 a 21:00 PM
                and 'salida' in str(r.get(tipo_col, '')).lower()
                and not ('horas extra' in str(r.get(tipo_col, '')).lower() or 'he' in str(r.get(tipo_col, '')).lower())
            ]
            if evening_swipes_salida:
                try:
                    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
                    fecha_next_str = (fecha_dt + timedelta(days=1)).strftime('%Y-%m-%d')
                    next_day_swipes = df_marcaciones[
                        (df_marcaciones['DNI_STR'].apply(lambda d: str(d).strip().lstrip('0')) == dni_clean) &
                        (df_marcaciones['Fecha_Clean'] == fecha_next_str)
                    ]
                    has_next_morning_exit = any(
                        time_to_seconds(r['Hora_Clean']) <= 32400 # <= 09:00 AM
                        for _, r in next_day_swipes.iterrows()
                    )
                    if has_next_morning_exit:
                        valid_rows.loc[evening_swipes_salida[0], tipo_col] = 'Registro de entrada'
                except Exception:
                    pass

        # Dividir sub-bloques de turno si existe un reingreso (SEGUNDA ENTRADA) después de las 16:00 PM (Caso Cambio de Guardia / Medio Día previo - Punto 4)
        morning_entries = [
            r for _, r in valid_rows.iterrows() 
            if 'entrada' in str(r.get(tipo_col, '')).strip().lower() 
            and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower()) 
            and r['Hora_Clean'] is not None and time_to_seconds(r['Hora_Clean']) < 43200
        ]
        late_night_entries = [
            r for _, r in valid_rows.iterrows() 
            if 'entrada' in str(r.get(tipo_col, '')).strip().lower() 
            and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower()) 
            and r['Hora_Clean'] is not None and time_to_seconds(r['Hora_Clean']) >= 57600 # >= 16:00 PM
        ]

        sub_blocks = []
        if morning_entries and late_night_entries:
            cut_sec = time_to_seconds(late_night_entries[0]['Hora_Clean']) - 60 # Cortar justo antes de la entrada nocturna
            block1 = valid_rows[valid_rows['Hora_Clean'].apply(lambda h: time_to_seconds(h) < cut_sec)]
            block2 = valid_rows[valid_rows['Hora_Clean'].apply(lambda h: time_to_seconds(h) >= cut_sec)]
            if not block1.empty: sub_blocks.append(block1)
            if not block2.empty: sub_blocks.append(block2)
        else:
            sub_blocks = [valid_rows]

        for current_block in sub_blocks:
            times = current_block['Hora_Clean'].tolist()

            entrada = None
            salida = None
            he_explicita_total_min = 0
            incidencias_list = []

            # 1. Detectar entradas múltiples / duplicadas dentro del mismo bloque (Solo en intervalos cortos de <= 15 min)
            entradas_rows = [
                r['Hora_Clean'] for _, r in current_block.iterrows()
                if 'entrada' in str(r.get(tipo_col, '')).strip().lower() and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower())
            ]
            if entradas_rows:
                entradas_rows.sort(key=lambda t: time_to_seconds(t))
        
            tiene_entrada_duplicada = False
            hora_entrada_duplicada_str = ""
            if len(entradas_rows) > 1:
                duplicadas_cercanas = [
                    t for t in entradas_rows[1:] 
                    if 0 < (time_to_seconds(t) - time_to_seconds(entradas_rows[0])) <= 900 # <= 15 minutos
                ]
                if duplicadas_cercanas:
                    tiene_entrada_duplicada = True
                    hora_entrada_duplicada_str = ", ".join([t.strftime('%H:%M') for t in duplicadas_cercanas])

            # 2. Detectar entrada, salida principal y marcaciones de Horas Extra
            has_explicit_entrada = False
            has_explicit_salida = False
            he_start = None
            he_end = None

            for _, r in current_block.iterrows():
                tipo_pase = str(r.get(tipo_col, '')).strip().lower()
                h = r['Hora_Clean']
                
                if 'entrada' in tipo_pase and not ('horas extra' in tipo_pase or 'he' in tipo_pase):
                    has_explicit_entrada = True
                    if entrada is None:
                        entrada = h
                elif 'salida' in tipo_pase and not ('horas extra' in tipo_pase or 'he' in tipo_pase):
                    has_explicit_salida = True
                    if salida is None or h > salida:
                        salida = h
                elif ('inicio' in tipo_pase and ('horas extra' in tipo_pase or 'he' in tipo_pase)) or 'inicio de horas extra' in tipo_pase:
                    he_start = h
                elif ('fin' in tipo_pase and ('horas extra' in tipo_pase or 'he' in tipo_pase)) or 'fin de horas extra' in tipo_pase:
                    he_end = h

            # Resetear salida si ocurrió ANTES de la entrada en la misma fecha
            if entrada and salida and time_to_seconds(salida) <= time_to_seconds(entrada):
                salida = None
                has_explicit_salida = False

            # Búsqueda cruzada de medianoche para Fin de Horas Extra
            he_end_fecha = fecha
            if he_start and not he_end:
                try:
                    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
                    fecha_next_str = (fecha_dt + timedelta(days=1)).strftime('%Y-%m-%d')
                    next_day_he_swipes = df_marcaciones[
                        (df_marcaciones['DNI_STR'].apply(lambda d: str(d).strip().lstrip('0')) == dni_clean) &
                        (df_marcaciones['Fecha_Clean'] == fecha_next_str)
                    ]
                    he_fin_next_rows = [
                        r for _, r in next_day_he_swipes.iterrows()
                        if ('fin' in str(r.get(tipo_col, '')).strip().lower() and ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower()))
                        or 'fin de horas extra' in str(r.get(tipo_col, '')).strip().lower()
                    ]
                    if he_fin_next_rows:
                        he_fin_next_rows.sort(key=lambda r: time_to_seconds(r['Hora_Clean']))
                        he_end = he_fin_next_rows[0]['Hora_Clean']
                        he_end_fecha = fecha_next_str
                        consumed_swipes.add((dni_clean, fecha_next_str, he_end.strftime('%H:%M')))
                except Exception as e:
                    pass

            if he_start and he_end:
                i_sec = time_to_seconds(he_start)
                f_sec = time_to_seconds(he_end)
                dur_block_min = ((86400 - i_sec) + f_sec) // 60 if he_end_fecha != fecha else ((f_sec - i_sec) // 60 if f_sec >= i_sec else ((86400 - i_sec) + f_sec) // 60)
                if dur_block_min > 0:
                    he_explicita_total_min += dur_block_min
                    horario_tmp = detectar_horario(entrada or salida, is_salida_only=(entrada is None and salida is not None), config=config)
                    rows_horas_extra.append({
                        'FECHA': fecha, 'DNI': dni, 'APELLIDOS': worker_info.get('APELLIDOS', ''),
                        'NOMBRES': worker_info.get('NOMBRES', ''),
                        'CARGO': worker_info.get('CARGO', ''),
                        'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                        'TURNO': horario_tmp,
                        'FECHA_INICIO_HE': fecha,
                        'INICIO H.E.': he_start.strftime('%H:%M'),
                        'FECHA_FIN_HE': he_end_fecha,
                        'FIN H.E.': he_end.strftime('%H:%M'),
                        'DURACIÓN (HH:MM)': format_hhmm_str(dur_block_min, is_hours_float=False),
                        'DURACIÓN': dur_block_min,
                        'OBSERVACIÓN': f'Horas extra marcadas en biométrico ({fecha} -> {he_end_fecha})' if he_end_fecha != fecha else 'Horas extra marcadas en biométrico'
                    })

            # Fallback marcaciones genéricas
            if not has_explicit_entrada and not has_explicit_salida and len(times) > 0:
                entrada = times[0]
                if len(times) > 1:
                    salida = times[-1]

            # Detectar Horario (DÍA vs NOCHE)
            hora_ref = entrada if entrada is not None else salida
            horario = detectar_horario(hora_ref, is_salida_only=(entrada is None and salida is not None), config=config)

            # Búsqueda cruzada de medianoche para TURNO NOCHE o entrada >= 16:00
            fecha_entrada = fecha
            fecha_salida = fecha

            if entrada and (salida is None or time_to_seconds(salida) <= time_to_seconds(entrada)):
                if horario == 'NOCHE' or time_to_seconds(entrada) >= 57600: # >= 16:00 PM
                    try:
                        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
                        fecha_next_str = (fecha_dt + timedelta(days=1)).strftime('%Y-%m-%d')
                        next_day_swipes = df_marcaciones[
                            (df_marcaciones['DNI_STR'].apply(lambda d: str(d).strip().lstrip('0')) == dni_clean) &
                            (df_marcaciones['Fecha_Clean'] == fecha_next_str)
                        ]
                        salida_next_rows = [
                            r for _, r in next_day_swipes.iterrows()
                            if 'salida' in str(r.get(tipo_col, '')).strip().lower() and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower())
                            and r['Hora_Clean'] is not None and time_to_seconds(r['Hora_Clean']) <= 43200
                        ]
                        if salida_next_rows:
                            salida_next_rows.sort(key=lambda r: time_to_seconds(r['Hora_Clean']))
                            salida = salida_next_rows[0]['Hora_Clean']
                            fecha_salida = fecha_next_str
                            consumed_swipes.add((dni_clean, fecha_next_str, salida.strftime('%H:%M')))
                    except Exception as e:
                        pass

            cargo_val = str(worker_info.get('CARGO', worker_info.get('Posición', ''))).strip().lower()
            # Estricto: Solo aplica si el cargo/posición contiene exactamente 'Mantenimiento' (como Josmell, Edin, Franco, etc.)
            es_mantenimiento = "mantenimiento" in cargo_val

            # Cálculo de horas trabajadas (Regla Mantenimiento 06:25 AM vs Candado General 07:00/19:00)
            horas_trabajadas = 0.0
            if entrada and salida:
                e_sec = time_to_seconds(entrada)
                s_sec = time_to_seconds(salida)

                e_effective_sec = e_sec

                if es_mantenimiento:
                    # Mantenimiento: Si entra ANTES de las 06:25 AM, considerar marcación real de entrada
                    # Si entra entre 06:25 AM y 07:00 AM, considerar inicio oficial 07:00 AM
                    if e_sec < 6 * 3600 + 25 * 60:
                        e_effective_sec = e_sec
                    elif 6 * 3600 + 25 * 60 <= e_sec < 7 * 3600:
                        e_effective_sec = 7 * 3600
                    elif e_sec < 18 * 3600 + 25 * 60:
                        e_effective_sec = e_sec
                    elif 18 * 3600 + 25 * 60 <= e_sec < 19 * 3600:
                        e_effective_sec = 19 * 3600
                    elif 4 * 3600 <= e_sec < 5 * 3600:
                        e_effective_sec = 5 * 3600
                    elif 16 * 3600 <= e_sec < 17 * 3600:
                        e_effective_sec = 17 * 3600
                else:
                    # Para las demás posiciones: Candado oficial 07:00 AM / 19:00 PM
                    if 6 * 3600 <= e_sec < 7 * 3600:
                        e_effective_sec = 7 * 3600
                    elif 18 * 3600 <= e_sec < 19 * 3600:
                        e_effective_sec = 19 * 3600
                    elif 4 * 3600 <= e_sec < 5 * 3600:
                        e_effective_sec = 5 * 3600
                    elif 16 * 3600 <= e_sec < 17 * 3600:
                        e_effective_sec = 17 * 3600

                if fecha_salida != fecha_entrada or s_sec < e_effective_sec:
                    dur_sec = (86400 - e_effective_sec) + s_sec
                else:
                    dur_sec = s_sec - e_effective_sec
                horas_trabajadas = round(dur_sec / 3600.0, 2)

            # Identificar Media Jornada / Jornada Parcial (Punto 3: Formato conciso Jornada Parcial (hh:mm))
            es_media_jornada = False
            if 5.0 <= horas_trabajadas <= 8.0:
                es_media_jornada = True

            # Identificar Cambio de Guardia / Relevo Cuadrilla (Ventana de Relevo Día: 04:30-06:00 AM, Relevo Noche: 16:30-18:00 PM)
            es_cambio_guardia = False
            if entrada and salida and not es_mantenimiento:
                e_sec = time_to_seconds(entrada)
                s_sec = time_to_seconds(salida)
                if (4 * 3600 + 30 * 60 <= e_sec <= 6 * 3600) or \
                   (4 * 3600 + 30 * 60 <= s_sec <= 6 * 3600) or \
                   (16 * 3600 + 30 * 60 <= e_sec <= 18 * 3600) or \
                   (16 * 3600 + 30 * 60 <= s_sec <= 18 * 3600):
                    es_cambio_guardia = True

            # 3. Validar Marcación Faltante
            marcacion_faltante_str = ""
            if entrada and not salida and len(times) == 1:
                marcacion_faltante_str = "Falta marcación de salida"
            elif not entrada and salida:
                marcacion_faltante_str = f"Salida sin registro de entrada previa ({salida.strftime('%H:%M')})"

            # 4. Calcular Tardanza
            tardanza_min = calcular_tardanza(horario, entrada, config, es_media_jornada=es_media_jornada)

            # 5. Calcular Salida Anticipada
            salida_ant_min = calcular_salida_anticipada(horario, salida, entrada, config)
            if es_cambio_guardia:
                salida_ant_min = 0

            # 6. Exceso de Jornada (Punto 1: Lógica General >= 30 min para TODOS)
            if es_cambio_guardia or es_media_jornada:
                exceso_jornada_min = 0
            # 6. Exceso de Jornada (Punto 1: Lógica General >= 30 min para TODOS)
            if es_cambio_guardia or es_media_jornada:
                exceso_jornada_min = 0
            elif horas_trabajadas > 12.0:
                exceso_jornada_min = int(round((horas_trabajadas - 12.0) * 60))
            else:
                exceso_jornada_min = 0

            if exceso_jornada_min < 30:
                exceso_jornada_min_reporte = 0
            else:
                exceso_jornada_min_reporte = exceso_jornada_min

            total_horas_adicionales_min = exceso_jornada_min_reporte + he_explicita_total_min

            # Regla especial DNI 46181231 (José Moncada): Horarios libres, siempre registro Normal, sin observaciones
            is_dni_46181231 = (str(dni_clean).strip() == "46181231")
            if is_dni_46181231:
                tardanza_min = 0
                salida_ant_min = 0
                exceso_jornada_min = 0
                exceso_jornada_min_reporte = 0
                total_horas_adicionales_min = he_explicita_total_min
                incidencias_list = []
                incidencias_str = ""
                tipo_registro = "Normal"
            else:
                # CONSTRUCCIÓN ORDENADA Y DESDUPLICADA DE LA COLUMNA OBSERVACIÓN / INCIDENCIAS
                # 1. Horas extras explícitas (botones biométrico) - PRIMERO
                if he_explicita_total_min > 0:
                    incidencias_list.append(f"Horas extras ({format_hhmm_str(he_explicita_total_min, is_hours_float=False)})")

                # 2. Exceso de Jornada (si es >= 30 min)
                if exceso_jornada_min_reporte >= 30:
                    incidencias_list.append(f"Exceso de Jornada ({format_hhmm_str(exceso_jornada_min_reporte, is_hours_float=False)})")

                # 3. Jornada Parcial (Medio día) (hh:mm) en Observación
                if es_media_jornada:
                    incidencias_list.append(f"Jornada parcial (Medio día) ({format_hhmm_str(int(round(horas_trabajadas * 60)), is_hours_float=False)})")

                # 4. Salida Anticipada
                if salida_ant_min > 0 and not es_media_jornada:
                    incidencias_list.append(f"Salida anticipada ({format_hhmm_str(salida_ant_min, is_hours_float=False)})")

                # 5. Marcación Faltante
                if marcacion_faltante_str:
                    incidencias_list.append(marcacion_faltante_str)

                # 6. Entrada Duplicada (solo si es intervalo corto <= 15 min)
                if tiene_entrada_duplicada and hora_entrada_duplicada_str:
                    incidencias_list.append(f"Entrada duplicada ({hora_entrada_duplicada_str})")

                # 7. Tardanza en Observación (siempre que exista tardanza > 0)
                if tardanza_min > 0:
                    incidencias_list.append(f"Tardanza ({format_hhmm_str(tardanza_min, is_hours_float=False)})")

                # Desduplicar manteniendo el orden de prioridad
                incidencias_list = list(dict.fromkeys(incidencias_list))
                incidencias_str = ", ".join(incidencias_list) if incidencias_list else ""

                # Poblar tabla detallada de incidencias
                for inc_item in incidencias_list:
                    sev = 'ALTA' if ('omitid' in inc_item.lower() or 'pendiente' in inc_item.lower()) else ('MEDIA' if 'tardanza' in inc_item.lower() else 'BAJA')
                    rows_incidencias.append({
                        'FECHA': fecha,
                        'DNI': dni_export,
                        'APELLIDOS': worker_info.get('APELLIDOS', ''),
                        'NOMBRES': worker_info.get('NOMBRES', ''),
                        'CARGO': worker_info.get('CARGO', ''),
                        'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                        'TIPO': 'ASISTENCIA',
                        'HORA': entrada.strftime('%H:%M') if entrada else (salida.strftime('%H:%M') if salida else '-'),
                        'DESCRIPCIÓN': inc_item,
                        'SEVERIDAD': sev,
                        'OBSERVACIÓN': ''
                    })
                
                # Clasificación de Tipo Registro (Columna U)
                has_exceso = exceso_jornada_min_reporte >= 30
                has_he = he_explicita_total_min > 0

                # Punto 2: Si tiene exceso de jornada y horas extras a la vez, solo considerar Horas extras
                if has_he:
                    tipo_registro = "Horas extras"
                elif has_exceso:
                    tipo_registro = "Exceso de Jornada"
                elif not entrada and salida:
                    tipo_registro = "Entrada pendiente"
                elif entrada and not salida:
                    tipo_registro = "Salida pendiente"
                elif es_media_jornada:
                    tipo_registro = "Cambio de guardia"
                elif es_cambio_guardia:
                    tipo_registro = "Cambio de guardia"
                elif salida_ant_min > 0:
                    tipo_registro = "Salida anticipada"
                else:
                    tipo_registro = "Normal"

                # Regla Tardanza en Columna U: Si la tardanza es > 30 minutos, colocar /Tardanza en Tipo Registro
                if tardanza_min > 30:
                    if tipo_registro == "Normal":
                        tipo_registro = "Tardanza"
                    else:
                        tipo_registro = f"{tipo_registro}/Tardanza"

            estado = calcular_estado_asistencia(
                tiene_entrada=(entrada is not None),
                tiene_salida=(salida is not None),
                tardanza=tardanza_min,
                salida_ant=salida_ant_min,
                incidencias=incidencias_str,
                total_horas_adic_min=total_horas_adicionales_min
            )
            
            f_inicio_he = fecha if he_start else "-"
            h_inicio_he = he_start.strftime('%H:%M') if he_start else "-"
            f_fin_he = he_end_fecha if he_end else "-"
            h_fin_he = he_end.strftime('%H:%M') if he_end else "-"

            rows_asistencia.append({
                'FECHA': fecha,
                'FECHA_ENTRADA': fecha_entrada,
                'FECHA_SALIDA': fecha_salida,
                'DNI': dni_export,
                'APELLIDOS': worker_info.get('APELLIDOS', ''),
                'NOMBRES': worker_info.get('NOMBRES', ''),
                'CARGO': worker_info.get('CARGO', ''),
                'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                'TURNO': horario,
                'ENTRADA': entrada.strftime('%H:%M') if entrada else None,
                'SALIDA': salida.strftime('%H:%M') if salida else None,
                'FECHA_INICIO_HE': f_inicio_he,
                'HORA_INICIO_HE': h_inicio_he,
                'FECHA_FIN_HE': f_fin_he,
                'HORA_FIN_HE': h_fin_he,
                'HORAS DE TURNO (HH:MM)': format_hhmm_str(horas_trabajadas, is_hours_float=True),
                'EXCESO DE TURNO (HH:MM)': format_hhmm_str(exceso_jornada_min_reporte, is_hours_float=False),
                'HORAS EXTRAS (HH:MM)': format_hhmm_str(he_explicita_total_min, is_hours_float=False),
                'TOTAL DE HORAS ADICIONALES (HH:MM)': format_hhmm_str(total_horas_adicionales_min, is_hours_float=False),
                'TARDANZA (HH:MM)': format_hhmm_str(tardanza_min, is_hours_float=False),
                'SALIDA ANTICIPADA (HH:MM)': format_hhmm_str(salida_ant_min, is_hours_float=False),
                'HORAS DE TURNO': horas_trabajadas,
                'HORAS TRABAJADAS': horas_trabajadas,
                'EXCESO DE TURNO': exceso_jornada_min_reporte,
                'EXCESO JORNADA': exceso_jornada_min_reporte,
                'HORAS EXTRAS': he_explicita_total_min,
                'TOTAL DE HORAS ADICIONALES': total_horas_adicionales_min,
                'TOTAL HORAS ADICIONALES': total_horas_adicionales_min,
                'TARDANZA (MIN)': tardanza_min,
                'SALIDA ANTICIPADA (MIN)': salida_ant_min,
                'TIPO_REGISTRO': tipo_registro,
                'INCIDENCIAS': incidencias_str,
                'ESTADO ASISTENCIA': estado,
                'OBSERVACIONES': 'Abastecer petróleo / Recoger personal / Varios' if (es_mantenimiento and entrada and time_to_seconds(entrada) < 6 * 3600 + 25 * 60) else ''
            })

    # Procesar FALTAS para trabajadores no registrados en las fechas del dataset
    for d in all_dates:
        for dni in all_dnis:
            if (dni, d) not in processed_keys:
                worker_info = workers_dict.get(dni, {})
                rows_asistencia.append({
                    'FECHA': d,
                    'DNI': dni,
                    'APELLIDOS': worker_info.get('APELLIDOS', ''),
                    'NOMBRES': worker_info.get('NOMBRES', ''),
                    'CARGO': worker_info.get('CARGO', ''),
                    'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                    'TURNO': 'N/A',
                    'ENTRADA': None,
                    'SALIDA': None,
                    'FECHA_INICIO_HE': '-',
                    'HORA_INICIO_HE': '-',
                    'FECHA_FIN_HE': '-',
                    'HORA_FIN_HE': '-',
                    'HORAS TRABAJADAS (HH:MM)': '00:00',
                    'TARDANZA (HH:MM)': '00:00',
                    'SALIDA ANTICIPADA (HH:MM)': '00:00',
                    'EXCESO JORNADA (HH:MM)': '00:00',
                    'TOTAL HORAS ADICIONALES (HH:MM)': '00:00',
                    'HORAS TRABAJADAS': 0.0,
                    'TARDANZA (MIN)': 0,
                    'SALIDA ANTICIPADA (MIN)': 0,
                    'EXCESO JORNADA': 0,
                    'TOTAL HORAS ADICIONALES': 0,
                    'INCIDENCIAS': '',
                    'ESTADO ASISTENCIA': 'FALTA',
                    'OBSERVACIONES': ''
                })

    df_res_asistencia = pd.DataFrame(rows_asistencia)
    df_res_horas_extra = pd.DataFrame(rows_horas_extra) if rows_horas_extra else pd.DataFrame(columns=['FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'ÁREA', 'TURNO', 'INICIO H.E.', 'FIN H.E.', 'DURACIÓN', 'OBSERVACIÓN'])
    df_res_incidencias = pd.DataFrame(rows_incidencias) if rows_incidencias else pd.DataFrame(columns=['FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'ÁREA', 'TIPO', 'HORA', 'DESCRIPCIÓN', 'SEVERIDAD', 'OBSERVACIÓN'])

    # KPIs ejecutivos
    total_personal = len(df_trabajadores)
    presentes = len(df_res_asistencia[df_res_asistencia['ESTADO ASISTENCIA'].isin(['ASISTIO', 'TARDANZA', 'SALIDA ANTICIPADA', 'TARDANZA + SALIDA ANTICIPADA', 'ASISTIO CON INCIDENCIAS', 'ASISTIO CON H.E.', 'SALIDA PENDIENTE'])])
    faltas = len(df_res_asistencia[df_res_asistencia['ESTADO ASISTENCIA'] == 'FALTA'])
    tardanzas = len(df_res_asistencia[df_res_asistencia['TARDANZA (MIN)'] > 0])
    incidencias_cnt = len(df_res_incidencias)
    turno_dia = len(df_res_asistencia[df_res_asistencia['TURNO'] == 'DIA'])
    turno_noche = len(df_res_asistencia[df_res_asistencia['TURNO'] == 'NOCHE'])
    
    kpis = {
        'total_personal': total_personal,
        'presentes': presentes,
        'faltas': faltas,
        'tardanzas': tardanzas,
        'incidencias': incidencias_cnt,
        'turno_dia': turno_dia,
        'turno_noche': turno_noche,
        'pct_asistencia': round((presentes / total_personal * 100) if total_personal > 0 else 0, 1)
    }

    return df_res_asistencia, df_res_horas_extra, df_res_incidencias, kpis
