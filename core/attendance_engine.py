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
    """Detecta si el horario corresponde a TURNO DÍA (07:00 - 19:00) o NOCHE (19:00 - 07:00)."""
    if hora_ref is None:
        return "DIA"
    
    h_sec = time_to_seconds(hora_ref)
    
    if is_salida_only:
        # Si la marcación es solo salida, entre las 11:00 y 23:59 corresponde al fin de TURNO DÍA
        if 11 * 3600 <= h_sec <= 23 * 3600 + 59 * 60:
            return "DIA"
        else:
            return "NOCHE"
    else:
        # Si la referencia es hora de entrada (05:00 a 16:59 es Turno Día)
        if 5 * 3600 <= h_sec < 17 * 3600:
            return "DIA"
        else:
            return "NOCHE"

def calcular_tardanza(horario: str, hora_entrada: time, config: AttendanceConfig) -> int:
    """
    Tardanza se calcula en minutos pasados los 15 minutos de tolerancia.
    Ejemplo: Entrada programada 07:00, límite tolerancia 07:15. Entrada 07:20 -> 5 min tardanza.
    """
    if hora_entrada is None:
        return 0
    
    hora_prog = time(7, 0) if horario == "DIA" else time(19, 0)
    prog_sec = time_to_seconds(hora_prog)
    limite_tolerancia_sec = prog_sec + (config.tolerancia_entrada_min * 60) # + 900s
    ent_sec = time_to_seconds(hora_entrada)
    
    if ent_sec <= limite_tolerancia_sec:
        return 0
    else:
        return int((ent_sec - limite_tolerancia_sec) // 60)


def calcular_salida_anticipada(horario: str, hora_salida: time, config: AttendanceConfig) -> int:
    """
    Salida anticipada aplica para ambos turnos con tolerancia de 10 min antes de la hora programada de salida.
    Turno Día: Salida programada 19:00, límite tolerancia 18:50. Salida antes de 18:50 genera salida anticipada.
    Turno Noche: Salida programada 07:00, límite tolerancia 06:50. Salida antes de 06:50 genera salida anticipada.
    Soporta salidas de madrugada al día siguiente (00:00 - 07:00 AM) descartándolas de salida anticipada.
    """
    if hora_salida is None:
        return 0
    
    hora_prog_salida = time(19, 0) if horario == "DIA" else time(7, 0)
    prog_salida_sec = time_to_seconds(hora_prog_salida)
    limite_tolerancia_salida_sec = prog_salida_sec - (config.tolerancia_salida_min * 60)
    sal_sec = time_to_seconds(hora_salida)
    
    if horario == "DIA":
        # Si salió después de las 18:50 (hasta las 23:59 o de madrugada 00:00 - 07:00 AM), no es salida anticipada
        if sal_sec >= limite_tolerancia_salida_sec or sal_sec <= time_to_seconds(time(7, 0)):
            return 0
        else:
            return int((limite_tolerancia_salida_sec - sal_sec) // 60)
    else: # NOCHE
        if sal_sec >= limite_tolerancia_salida_sec:
            return 0
        else:
            return int((limite_tolerancia_salida_sec - sal_sec) // 60)


def calcular_exceso_jornada(horario: str, hora_salida: time, config: AttendanceConfig) -> int:
    """
    Exceso de jornada en minutos para ambos turnos al salir después de la hora programada habitual (19:00 o 07:00).
    Soporta salidas de madrugada al día siguiente (ej. salida a la 01:00 AM en turno Día).
    """
    if hora_salida is None:
        return 0
        
    hora_prog_salida = time(19, 0) if horario == "DIA" else time(7, 0)
    prog_salida_sec = time_to_seconds(hora_prog_salida)
    sal_sec = time_to_seconds(hora_salida)
    
    if horario == "DIA":
        if sal_sec >= prog_salida_sec:
            return int((sal_sec - prog_salida_sec) // 60)
        elif sal_sec <= time_to_seconds(time(7, 0)): # Salió de madrugada al día siguiente (00:00 - 07:00 AM)
            return int(((86400 - prog_salida_sec) + sal_sec) // 60)
        return 0
    else: # TURNO NOCHE (salida programada 07:00 AM)
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
    # 1. Probar formato ISO YYYY-MM-DD
    try:
        dt = datetime.strptime(val_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    # 2. Probar formato Peruano DD/MM/YYYY
    try:
        dt = datetime.strptime(val_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    # 3. Fallback con dayfirst=True
    try:
        dt = pd.to_datetime(val_str, dayfirst=True)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return val_str

def procesar_asistencia_df(df_trabajadores: pd.DataFrame, df_marcaciones: pd.DataFrame, df_horas_extra_in: pd.DataFrame = None, config: AttendanceConfig = None) -> tuple:
    """
    Procesa marcaciones de Hikvision calculando la asistencia, horas extras e incidencias.
    Retorna (df_asistencia, df_horas_extra, df_incidencias, kpis_dict).
    """
    if config is None:
        config = AttendanceConfig()
        
    if df_trabajadores.empty or 'DNI' not in df_trabajadores.columns:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

    # Limpieza de DNI y construcción de mapa flexible que ignora ceros a la izquierda
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
    # Omitir filas de banner, DNI desalineado o marcaciones Indefinidas (reintentos o verificaciones fallidas)
    df_marcaciones = df_marcaciones[
        ~df_marcaciones['DNI_STR'].str.lower().str.contains('fecha:|semana:|periodo:|desconocido|none', regex=True, na=False)
    ]
    if tipo_col in df_marcaciones.columns:
        df_marcaciones = df_marcaciones[
            ~df_marcaciones[tipo_col].astype(str).str.lower().str.contains('indefinid', regex=True, na=False)
        ]
    
    # Deduplicar marcaciones estrictamente idénticas (mismo DNI, misma fecha, misma hora y mismo tipo)
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
    
    # Filtrar solo fechas válidas ISO YYYY-MM-DD
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

        # Dividir sub-bloques de turno si existe reingreso en el mismo día por cambio de cuadrilla (ej. entrada 06:48 mañana y entrada 18:41 noche)
        morning_entries = [r for _, r in valid_rows.iterrows() if 'entrada' in str(r.get(tipo_col, '')).strip().lower() and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower()) and r['Hora_Clean'] is not None and time_to_seconds(r['Hora_Clean']) < 43200]
        evening_entries = [r for _, r in valid_rows.iterrows() if 'entrada' in str(r.get(tipo_col, '')).strip().lower() and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower()) and r['Hora_Clean'] is not None and time_to_seconds(r['Hora_Clean']) >= 57600]

        sub_blocks = []
        if morning_entries and evening_entries:
            block1 = valid_rows[valid_rows['Hora_Clean'].apply(lambda h: time_to_seconds(h) < 57600)]
            block2 = valid_rows[valid_rows['Hora_Clean'].apply(lambda h: time_to_seconds(h) >= 57600)]
            if not block1.empty: sub_blocks.append(block1)
            if not block2.empty: sub_blocks.append(block2)
        else:
            sub_blocks = [valid_rows]

        for current_block in sub_blocks:
            times = current_block['Hora_Clean'].tolist()

            entrada = None
            salida = None
            current_he_start = None
            he_explicita_total_min = 0
            incidencias_list = []
            
            # 1. Detectar Entradas Múltiples / Duplicadas dentro del mismo bloque
            entradas_rows = [
                r['Hora_Clean'] for _, r in current_block.iterrows()
                if 'entrada' in str(r.get(tipo_col, '')).strip().lower() and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower())
            ]
        
            # Fallback para marcaciones genéricas: si no hay pases explícitos, considerar marcaciones dentro de los 30 min iniciales
            if not entradas_rows and len(times) > 1:
                first_sec = time_to_seconds(times[0])
                entradas_rows = [t for t in times if 0 <= (time_to_seconds(t) - first_sec) <= 1800 and t != times[-1]]

            if len(entradas_rows) > 1:
                h_dup_str = ", ".join([t.strftime('%H:%M') for t in entradas_rows[1:]])
                incidencias_list.append(f"Entrada duplicada ({h_dup_str})")
                rows_incidencias.append({
                    'FECHA': fecha, 'DNI': dni, 'APELLIDOS': worker_info.get('APELLIDOS', ''),
                    'NOMBRES': worker_info.get('NOMBRES', ''),
                    'CARGO': worker_info.get('CARGO', ''),
                    'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                    'TIPO': 'ENTRADA',
                    'HORA': entradas_rows[0].strftime('%H:%M'),
                    'DESCRIPCIÓN': f"Entrada duplicada ({h_dup_str})",
                    'SEVERIDAD': 'BAJA', 'OBSERVACIÓN': ''
                })

            # 2. Detectar entrada, salida principal y marcaciones explícitas de Horas Extra
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

            # Si la salida registrada ocurrió ANTES de la entrada en la misma fecha (ej. salida en la mañana a las 07:00 de un turno noche previo, y entrada en la tarde a las 18:31), resetear salida
            if entrada and salida and time_to_seconds(salida) <= time_to_seconds(entrada):
                salida = None
                has_explicit_salida = False

            # Búsqueda cruzada de medianoche para Fin de Horas Extra (Día N -> Día N+1)
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
                    print("EXCEPTION IN CROSS-DATE HE LOOKUP:", e)

            if he_start and he_end:
                i_sec = time_to_seconds(he_start)
                f_sec = time_to_seconds(he_end)
                if he_end_fecha != fecha:
                    dur_block_min = ((86400 - i_sec) + f_sec) // 60
                else:
                    dur_block_min = (f_sec - i_sec) // 60 if f_sec >= i_sec else ((86400 - i_sec) + f_sec) // 60

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

            # Fallback SOLO si no hay pases explícitos (marcaciones genéricas)
            if not has_explicit_entrada and not has_explicit_salida and len(times) > 0:
                entrada = times[0]
                if len(times) > 1:
                    salida = times[-1]

            # Detectar Horario (DÍA vs NOCHE) usando la referencia disponible (entrada o salida)
            hora_ref = entrada if entrada is not None else salida
            horario = detectar_horario(hora_ref, is_salida_only=(entrada is None and salida is not None), config=config)

            # Búsqueda de salida cruzando medianoche para Turno NOCHE (día N -> día N+1)
            fecha_entrada = fecha
            fecha_salida = fecha

            if entrada and (salida is None or time_to_seconds(salida) <= time_to_seconds(entrada)):
                if horario == 'NOCHE' or time_to_seconds(entrada) >= 61200: # >= 17:00
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
                        print("EXCEPTION IN NIGHT SHIFT LOOKUP:", e)

            # 3. Validar Marcación Faltante
            if entrada and not salida and len(times) == 1:
                incidencias_list.append("Falta marcación de salida")
                rows_incidencias.append({
                    'FECHA': fecha, 'DNI': dni, 'APELLIDOS': worker_info.get('APELLIDOS', ''),
                    'NOMBRES': worker_info.get('NOMBRES', ''),
                    'CARGO': worker_info.get('CARGO', ''),
                    'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                    'TIPO': 'SALIDA',
                    'HORA': entrada.strftime('%H:%M'),
                    'DESCRIPCIÓN': f"Marcación de entrada registrada a las {entrada.strftime('%H:%M')} sin marcación de salida",
                    'SEVERIDAD': 'ALTA', 'OBSERVACIÓN': ''
                })
            elif not entrada and salida:
                incidencias_list.append(f"Salida sin registro de entrada previa ({salida.strftime('%H:%M')})")
                rows_incidencias.append({
                    'FECHA': fecha, 'DNI': dni, 'APELLIDOS': worker_info.get('APELLIDOS', ''),
                    'NOMBRES': worker_info.get('NOMBRES', ''),
                    'CARGO': worker_info.get('CARGO', ''),
                    'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                    'TIPO': 'ENTRADA',
                    'HORA': salida.strftime('%H:%M'),
                    'DESCRIPCIÓN': f"Salida registrada a las {salida.strftime('%H:%M')} sin registro de entrada previa",
                    'SEVERIDAD': 'ALTA', 'OBSERVACIÓN': ''
                })

            # 4. Calcular Tardanza
            tardanza_min = calcular_tardanza(horario, entrada, config)
            if tardanza_min > 0:
                incidencias_list.append(f"Tardanza ({tardanza_min} min)")
                rows_incidencias.append({
                    'FECHA': fecha, 'DNI': dni, 'APELLIDOS': worker_info.get('APELLIDOS', ''),
                    'NOMBRES': worker_info.get('NOMBRES', ''),
                    'CARGO': worker_info.get('CARGO', ''),
                    'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                    'TIPO': 'ENTRADA',
                    'HORA': entrada.strftime('%H:%M'),
                    'DESCRIPCIÓN': f"Tardanza de {tardanza_min} minutos (Entrada: {entrada.strftime('%H:%M')})",
                    'SEVERIDAD': 'BAJA', 'OBSERVACIÓN': ''
                })

            # 5. Calcular Salida Anticipada
            salida_ant_min = calcular_salida_anticipada(horario, salida, config)
            if salida_ant_min > 0:
                incidencias_list.append(f"Salida anticipada ({salida_ant_min} min)")
                rows_incidencias.append({
                    'FECHA': fecha, 'DNI': dni, 'APELLIDOS': worker_info.get('APELLIDOS', ''),
                    'NOMBRES': worker_info.get('NOMBRES', ''),
                    'CARGO': worker_info.get('CARGO', ''),
                    'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                    'TIPO': 'SALIDA',
                    'HORA': salida.strftime('%H:%M'),
                    'DESCRIPCIÓN': f"Salida anticipada de {salida_ant_min} minutos (Salida: {salida.strftime('%H:%M')})",
                    'SEVERIDAD': 'MEDIA', 'OBSERVACIÓN': ''
                })

            # 6. Calcular Exceso de Jornada (Solo si hubo entrada registrada)
            exceso_jornada_min = calcular_exceso_jornada(horario, salida, config) if entrada is not None else 0

            # 7. Validar Límite de Exceso de Jornada (> 60 min)
            if exceso_jornada_min > config.max_exceso_jornada_min:
                h_sal_str = salida.strftime('%H:%M') if salida else ''
                incidencias_list.append(f"Exceso de jornada no autorizado ({exceso_jornada_min} min)")
                rows_incidencias.append({
                    'FECHA': fecha, 'DNI': dni, 'APELLIDOS': worker_info.get('APELLIDOS', ''),
                    'NOMBRES': worker_info.get('NOMBRES', ''),
                    'CARGO': worker_info.get('CARGO', ''),
                    'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                    'TIPO': 'SALIDA',
                    'HORA': h_sal_str,
                    'DESCRIPCIÓN': f"Exceso de jornada no autorizado ({h_sal_str} - Exceso {exceso_jornada_min} min)",
                    'SEVERIDAD': 'MEDIA', 'OBSERVACIÓN': ''
                })

            total_horas_adicionales_min = exceso_jornada_min + he_explicita_total_min

            # Cálculo de horas trabajadas
            horas_trabajadas = 0.0
            if entrada and salida:
                e_sec = time_to_seconds(entrada)
                s_sec = time_to_seconds(salida)
                if s_sec >= e_sec:
                    dur_sec = s_sec - e_sec
                else:
                    dur_sec = (86400 - e_sec) + s_sec
                horas_trabajadas = round(dur_sec / 3600.0, 2)

                # Detección de Jornada Parcial (~6h / Trabajo Medio Día: entre 5.0h y 8.0h)
                if 5.0 <= horas_trabajadas <= 8.0:
                    incidencias_list.append(f"Jornada Parcial (Trabajo 6h - Medio Día: {horas_trabajadas}h)")

                # Detección de Cambio de Turno / Relevo de Cuadrilla
                # Caso 1: Salida Temprana de Relevo en Turno Día (Salida entre 16:15 y 17:45)
                if horario == 'DIA' and 58500 <= s_sec <= 63900: # 16:15 a 17:45 (5:00 PM)
                    incidencias_list.append(f"Cambio de Turno (Salida de Relevo a las {salida.strftime('%H:%M')})")
                # Caso 2: Entrada Temprana de Relevo en Turno Noche (Entrada entre 16:15 y 17:45, salida matutina 06:30-07:30)
                elif horario == 'NOCHE' and 58500 <= e_sec <= 63900: # 16:15 a 17:45 (5:00 PM)
                    incidencias_list.append(f"Cambio de Turno (Relevo de Cuadrilla - Entrada {entrada.strftime('%H:%M')})")
                
            incidencias_str = ", ".join(incidencias_list) if incidencias_list else ""
            estado = calcular_estado_asistencia(
                tiene_entrada=(entrada is not None),
                tiene_salida=(salida is not None),
                tardanza=tardanza_min,
                salida_ant=salida_ant_min,
                incidencias=incidencias_str,
                total_horas_adic_min=total_horas_adicionales_min
            )
            
            # Detalle de marcaciones H.E. (Inicio y Fin H.E. provienen EXCLUSIVAMENTE de marcaciones explícitas del biométrico)
            f_inicio_he = fecha if he_start else "-"
            h_inicio_he = he_start.strftime('%H:%M') if he_start else "-"
            f_fin_he = fecha if he_end else "-"
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
                'HORAS TRABAJADAS (HH:MM)': format_hhmm_str(horas_trabajadas, is_hours_float=True),
                'TARDANZA (HH:MM)': format_hhmm_str(tardanza_min, is_hours_float=False),
                'SALIDA ANTICIPADA (HH:MM)': format_hhmm_str(salida_ant_min, is_hours_float=False),
                'EXCESO JORNADA (HH:MM)': format_hhmm_str(exceso_jornada_min, is_hours_float=False),
                'TOTAL HORAS ADICIONALES (HH:MM)': format_hhmm_str(total_horas_adicionales_min, is_hours_float=False),
                'HORAS TRABAJADAS': horas_trabajadas,
                'TARDANZA (MIN)': tardanza_min,
                'SALIDA ANTICIPADA (MIN)': salida_ant_min,
                'EXCESO JORNADA': exceso_jornada_min,
                'TOTAL HORAS ADICIONALES': total_horas_adicionales_min,
                'INCIDENCIAS': incidencias_str,
                'ESTADO ASISTENCIA': estado,
                'OBSERVACIONES': ''
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
