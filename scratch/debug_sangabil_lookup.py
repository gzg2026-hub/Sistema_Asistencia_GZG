import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_datos_db
from core.attendance_engine import parse_date_val, parse_time_val, time_to_seconds, detectar_horario

_, df_marc, _, _, _ = obtener_datos_db()

df_marc['DNI_STR'] = df_marc['ID'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
df_marc['Fecha_Clean'] = df_marc['Fecha'].apply(parse_date_val)
df_marc['Hora_Clean'] = df_marc['Tiempo'].apply(parse_time_val)

sangabil = df_marc[df_marc['DNI_STR'].str.contains('48790853')]
print("--- MARCACIONES DE SANGABIL ---")
print(sangabil[['DNI_STR', 'Fecha_Clean', 'Hora_Clean', 'Tipo de pase de tarjeta']])

dni_clean = '48790853'
fecha_next_str = '2026-08-18'

next_day_swipes = df_marc[
    (df_marc['DNI_STR'].apply(lambda d: str(d).strip().lstrip('0')) == dni_clean) &
    (df_marc['Fecha_Clean'] == fecha_next_str)
]
print("\nMarcaciones del dia siguiente (2026-08-18):")
print(next_day_swipes[['DNI_STR', 'Fecha_Clean', 'Hora_Clean', 'Tipo de pase de tarjeta']])

tipo_col = 'Tipo de pase de tarjeta'
salida_next_rows = [
    r for _, r in next_day_swipes.iterrows()
    if 'salida' in str(r.get(tipo_col, '')).strip().lower() and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower())
    and r['Hora_Clean'] is not None and time_to_seconds(r['Hora_Clean']) <= 43200
]
print("\nSalida nocturna encontrada para el 18 en la mañana:", salida_next_rows)
