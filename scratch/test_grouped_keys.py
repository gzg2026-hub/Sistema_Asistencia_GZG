import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from core.attendance_engine import parse_date_val, parse_time_val, time_to_seconds, AttendanceConfig

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

# Step by step simulation of procesar_asistencia_df
df_marcaciones = df_marc.copy()
dni_col = 'ID' if 'ID' in df_marcaciones.columns else ('DNI' if 'DNI' in df_marcaciones.columns else df_marcaciones.columns[0])
df_marcaciones['DNI_STR'] = df_marcaciones[dni_col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

date_col = 'Fecha' if 'Fecha' in df_marcaciones.columns else 'FECHA'
df_marcaciones['Fecha_Clean'] = df_marcaciones[date_col].apply(parse_date_val)

time_col = 'Tiempo' if 'Tiempo' in df_marcaciones.columns else ('Hora' if 'Hora' in df_marcaciones.columns else 'HORA')
df_marcaciones['Hora_Clean'] = df_marcaciones[time_col].apply(parse_time_val)

tipo_col = 'Tipo de pase de tarjeta' if 'Tipo de pase de tarjeta' in df_marcaciones.columns else 'TIPO'
df_marcaciones = df_marcaciones[
    ~df_marcaciones['DNI_STR'].str.lower().str.contains('fecha:|semana:|periodo:|desconocido|none', regex=True, na=False)
]
if tipo_col in df_marcaciones.columns:
    df_marcaciones = df_marcaciones[
        ~df_marcaciones[tipo_col].astype(str).str.lower().str.contains('indefinid', regex=True, na=False)
    ]

grouped = df_marcaciones.groupby(['DNI_STR', 'Fecha_Clean'])

print("Claves en grouped:")
for (dni, fecha), group in grouped:
    if '48790853' in str(dni):
        print("  Key:", (dni, fecha), "Rows in group:", len(group))
