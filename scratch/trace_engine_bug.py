import sys
import os
import pandas as pd
from datetime import datetime, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from core.attendance_engine import parse_date_val, parse_time_val, time_to_seconds, AttendanceConfig

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

# Re-ejecutar manualmente el bloque del engine para Sangabil
config = AttendanceConfig()
df_marc = df_marc.copy()
dni_col = 'ID' if 'ID' in df_marc.columns else ('DNI' if 'DNI' in df_marc.columns else df_marc.columns[0])
df_marc['DNI_STR'] = df_marc[dni_col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

date_col = 'Fecha' if 'Fecha' in df_marc.columns else 'FECHA'
df_marc['Fecha_Clean'] = df_marc[date_col].apply(parse_date_val)

time_col = 'Tiempo' if 'Tiempo' in df_marc.columns else ('Hora' if 'Hora' in df_marc.columns else 'HORA')
df_marc['Hora_Clean'] = df_marc[time_col].apply(parse_time_val)

tipo_col = 'Tipo de pase de tarjeta' if 'Tipo de pase de tarjeta' in df_marc.columns else 'TIPO'
df_marc = df_marc[
    ~df_marc['DNI_STR'].str.lower().str.contains('fecha:|semana:|periodo:|desconocido|none', regex=True, na=False)
]
if tipo_col in df_marc.columns:
    df_marc = df_marc[
        ~df_marc[tipo_col].astype(str).str.lower().str.contains('indefinid', regex=True, na=False)
    ]

# Filtrar marcaciones de Sangabil
sangabil_df = df_marc[df_marc['DNI_STR'].str.contains('48790853')]
print("--- SANGABIL MARCACIONES EN ENGINE ---")
print(sangabil_df[['DNI_STR', 'Fecha_Clean', 'Hora_Clean', tipo_col]])

# Simular bucle para 2026-08-17
fecha = '2026-08-17'
dni = '48790853'
dni_clean = '48790853'
entrada = parse_time_val('18:50')
salida = None
horario = 'NOCHE'
consumed_swipes = set()

fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
fecha_next_str = (fecha_dt + timedelta(days=1)).strftime('%Y-%m-%d')

next_day_swipes = df_marc[
    (df_marc['DNI_STR'].apply(lambda d: str(d).strip().lstrip('0')) == dni_clean) &
    (df_marc['Fecha_Clean'] == fecha_next_str)
]
print("\nnext_day_swipes en df_marc:", len(next_day_swipes))
print(next_day_swipes[['DNI_STR', 'Fecha_Clean', 'Hora_Clean', tipo_col]])

salida_next_rows = [
    r for _, r in next_day_swipes.iterrows()
    if 'salida' in str(r.get(tipo_col, '')).strip().lower() and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower())
    and r['Hora_Clean'] is not None and time_to_seconds(r['Hora_Clean']) <= 43200
]
print("\nsalida_next_rows:", salida_next_rows)
