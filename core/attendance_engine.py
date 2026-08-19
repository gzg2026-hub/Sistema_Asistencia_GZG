from datetime import datetime, time
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

def detectar_horario(hora_entrada: time, config: AttendanceConfig) -> str:
    """Detecta si el horario corresponde a TURNO DÍA (07:00 - 19:00) o NOCHE (19:00 - 07:00)."""
    if hora_entrada is None:
        return "DIA" # Por defecto si no hay entrada
    
    h_sec = time_to_seconds(hora_entrada)
    start_dia = time_to_seconds(config.hora_inicio_dia) # 07:00 = 25200s
    end_dia = time_to_seconds(config.hora_fin_dia)       # 19:00 = 68400s
    
    # 05:00 a 16:59 se considera inicio de Turno Día
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

    # Limpieza de DNI
    df_trabajadores['DNI_STR'] = df_trabajadores['DNI'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    workers_dict = df_trabajadores.set_index('DNI_STR').to_dict(orient='index')
    
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
    
    # Filtrar solo fechas válidas ISO YYYY-MM-DD
    all_dates = [
        d for d in df_marcaciones['Fecha_Clean'].dropna().unique() 
        if d and isinstance(d, str) and len(d) == 10 and d[4] == '-' and d[7] == '-'
    ]
    all_dnis = [w for w in df_trabajadores['DNI_STR'].unique() if w and str(w).lower() != 'desconocido' and str(w).lower() != 'none']

    for (dni, fecha), group in grouped:
        if not fecha or not dni or len(fecha) != 10 or dni.lower() == 'desconocido' or 'fecha:' in dni.lower():
            continue
            
        processed_keys.add((dni, fecha))
        worker_info = workers_dict.get(dni, {
            'APELLIDOS': 'DESCONOCIDO',
            'NOMBRES': '',
            'CARGO': 'N/A',
            'AREA': 'N/A'
        })
        
        valid_rows = group.dropna(subset=['Hora_Clean']).sort_values('Hora_Clean')
        times = valid_rows['Hora_Clean'].tolist()

        entrada = None
        salida = None
        current_he_start = None
        he_explicita_total_min = 0
        incidencias_list = []
        
        # 1. Detectar Entradas Múltiples / Duplicadas
        # Filtrar solo marcaciones de tipo 'entrada' (omitiendo marcaciones de salida y horas extra)
        entradas_rows = [
            r['Hora_Clean'] for _, r in valid_rows.iterrows()
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

        # 2. Detectar entrada y salida principal
        for _, r in valid_rows.iterrows():
            tipo_pase = str(r.get(tipo_col, '')).strip().lower()
            h = r['Hora_Clean']
            
            if 'entrada' in tipo_pase and not ('horas extra' in tipo_pase or 'he' in tipo_pase):
                if entrada is None:
                    entrada = h
            elif 'salida' in tipo_pase and not ('horas extra' in tipo_pase or 'he' in tipo_pase):
                if salida is None or h > salida:
                    salida = h
            elif 'inicio' in tipo_pase and ('horas extra' in tipo_pase or 'he' in tipo_pase):
                current_he_start = h
            elif ('fin' in tipo_pase and ('horas extra' in tipo_pase or 'he' in tipo_pase)) or ('salida' in tipo_pase and current_he_start is not None):
                if current_he_start is not None:
                    i_sec = time_to_seconds(current_he_start)
                    f_sec = time_to_seconds(h)
                    dur_block_min = (f_sec - i_sec) // 60 if f_sec >= i_sec else ((86400 - i_sec) + f_sec) // 60
                    if dur_block_min > 0:
                        he_explicita_total_min += dur_block_min
                        horario_tmp = detectar_horario(entrada, config) if entrada else "DIA"
                        rows_horas_extra.append({
                            'FECHA': fecha, 'DNI': dni, 'APELLIDOS': worker_info.get('APELLIDOS', ''),
                            'NOMBRES': worker_info.get('NOMBRES', ''),
                            'CARGO': worker_info.get('CARGO', ''),
                            'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
                            'TURNO': horario_tmp,
                            'INICIO H.E.': current_he_start.strftime('%H:%M'),
                            'FIN H.E.': h.strftime('%H:%M'),
                            'DURACIÓN (HH:MM)': format_hhmm_str(dur_block_min, is_hours_float=False),
                            'DURACIÓN': dur_block_min,
                            'OBSERVACIÓN': 'Horas extra marcadas en biométrico'
                        })
                    current_he_start = None

        # Fallback si solo hay marcaciones genéricas
        if entrada is None and len(times) > 0:
            entrada = times[0]
        if salida is None and len(times) > 1:
            salida = times[-1]

        # Detectar Horario (DÍA vs NOCHE)
        horario = detectar_horario(entrada, config)

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

        # 6. Calcular Exceso de Jornada
        exceso_jornada_min = calcular_exceso_jornada(horario, salida, config)

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
            
        incidencias_str = ", ".join(incidencias_list) if incidencias_list else ""
        estado = calcular_estado_asistencia(
            tiene_entrada=(entrada is not None),
            tiene_salida=(salida is not None),
            tardanza=tardanza_min,
            salida_ant=salida_ant_min,
            incidencias=incidencias_str,
            total_horas_adic_min=total_horas_adicionales_min
        )
        
        # Detalle de marcaciones H.E. (Inicio y Fin H.E.)
        f_inicio_he = "-"
        h_inicio_he = "-"
        punto_inicio_he = "-"
        f_fin_he = "-"
        h_fin_he = "-"
        punto_fin_he = "-"

        if exceso_jornada_min > 0 and salida is not None:
            f_inicio_he = fecha
            h_inicio_he = "19:00" if horario == "DIA" else "07:00"
            punto_inicio_he = "Garita Biometrico_wifi-1"
            f_fin_he = fecha
            h_fin_he = salida.strftime('%H:%M')
            punto_fin_he = "Planta_biometrico_wifi-1"

        rows_asistencia.append({
            'FECHA': fecha,
            'DNI': dni,
            'APELLIDOS': worker_info.get('APELLIDOS', ''),
            'NOMBRES': worker_info.get('NOMBRES', ''),
            'CARGO': worker_info.get('CARGO', ''),
            'ÁREA': worker_info.get('AREA', worker_info.get('ÁREA', '')),
            'TURNO': horario,
            'ENTRADA': entrada.strftime('%H:%M') if entrada else None,
            'SALIDA': salida.strftime('%H:%M') if salida else None,
            'FECHA_INICIO_HE': f_inicio_he,
            'HORA_INICIO_HE': h_inicio_he,
            'PUNTO_INICIO_HE': punto_inicio_he,
            'FECHA_FIN_HE': f_fin_he,
            'HORA_FIN_HE': h_fin_he,
            'PUNTO_FIN_HE': punto_fin_he,
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
                    'PUNTO_INICIO_HE': '-',
                    'FECHA_FIN_HE': '-',
                    'HORA_FIN_HE': '-',
                    'PUNTO_FIN_HE': '-',
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
