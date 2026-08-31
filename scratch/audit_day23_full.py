import sys, os
sys.path.insert(0, os.getcwd())
import pandas as pd
from core.attendance_engine import procesar_asistencia_df, parse_date_val, parse_time_val

df_raw = pd.read_excel('downloads/data_cruda/Transacciones_Acumuladas.xlsx')
df_padron = pd.read_excel('Padron_Trabajadores_GZG.xlsx', header=2)

df_asistencia, df_he, df_inc, kpis = procesar_asistencia_df(df_padron, df_raw)

# Filter for date 2026-08-23
df_23 = df_asistencia[df_asistencia['FECHA'].astype(str).str.contains('2026-08-23')].copy()

print(f"=== AUDITORÍA COMPLETA DÍA CERRADO 23/08/2026 ({len(df_23)} TRABAJADORES) ===")

anomalies = []

for idx, row in df_23.iterrows():
    dni = str(row['DNI']).strip().lstrip('0').zfill(8)
    apellidos = str(row.get('APELLIDOS', ''))
    nombres = str(row.get('NOMBRES', ''))
    turno = str(row.get('TURNO', ''))
    entrada = str(row.get('ENTRADA', ''))
    salida = str(row.get('SALIDA', ''))
    horas = str(row.get('HORAS DE TURNO (HH:MM)', '00:00'))
    tardanza = str(row.get('TARDANZA (HH:MM)', '00:00'))
    exceso = str(row.get('EXCESO DE TURNO (HH:MM)', '00:00'))
    he = str(row.get('HORAS EXTRAS (HH:MM)', '00:00'))
    estado = str(row.get('ESTADO ASISTENCIA', ''))
    tipo_reg = str(row.get('TIPO_REGISTRO', ''))
    incidencias = str(row.get('INCIDENCIAS', ''))
    obs = str(row.get('OBSERVACIONES', ''))

    # Check raw transactions for this worker on 23 and 24
    raw_23_24 = df_raw[
        (df_raw['ID'].astype(str).str.strip().str.lstrip('0').str.zfill(8) == dni) &
        (df_raw['Fecha'].apply(parse_date_val).isin(['2026-08-23', '2026-08-24']))
    ].sort_values(['Fecha', 'Tiempo'])

    swipes_str = ", ".join([
        f"{r['Fecha']} {r['Tiempo']} ({r['Tipo de pase de tarjeta']})"
        for _, r in raw_23_24.iterrows()
    ])

    # Potential anomaly checks
    is_anomaly = False
    reasons = []

    if estado == 'SALIDA PENDIENTE':
        is_anomaly = True
        reasons.append("SALIDA PENDIENTE")

    if estado == 'FALTA' and len(raw_23_24[raw_23_24['Fecha'].apply(parse_date_val) == '2026-08-23']) > 0:
        is_anomaly = True
        reasons.append("Tiene marcación el 23 pero fue marcado como FALTA")

    if entrada != 'None' and entrada != '' and (salida == 'None' or salida == '' or salida == 'nan'):
        is_anomaly = True
        reasons.append("Entrada registrada pero Salida nula/vacía")

    if 'mantenimiento' in str(row.get('CARGO', '')).lower() and entrada != 'None':
        # Check maintenance entry rule
        pass

    if is_anomaly or True: # Print summary table line for everyone first
        print(f"DNI: {dni} | {apellidos} {nombres} | Turno: {turno} | Ent: {entrada} | Sal: {salida} | Hrs: {horas} | Est: {estado} | Flag: {', '.join(reasons) if reasons else 'OK'}")

print("\n=== RESUMEN DE OBSERVACIONES / ANOMALÍAS ENCONTRADAS ===")
count_ok = 0
for idx, row in df_23.iterrows():
    dni = str(row['DNI']).strip().lstrip('0').zfill(8)
    apellidos = str(row.get('APELLIDOS', ''))
    nombres = str(row.get('NOMBRES', ''))
    entrada = str(row.get('ENTRADA', ''))
    salida = str(row.get('SALIDA', ''))
    estado = str(row.get('ESTADO ASISTENCIA', ''))
    if estado == 'SALIDA PENDIENTE' or (entrada and entrada != 'None' and (not salida or salida == 'None')):
        print(f"⚠️ REVISAR: {dni} {apellidos} {nombres} - Estado: {estado}, Entrada: {entrada}, Salida: {salida}")
    else:
        count_ok += 1

print(f"Total registros analizados: {len(df_23)} | Sin observaciones: {count_ok}")
