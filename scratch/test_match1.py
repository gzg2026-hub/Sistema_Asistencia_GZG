import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_datos_db
from core.attendance_engine import parse_date_val, parse_time_val, time_to_seconds

_, df_marc, _, _, _ = obtener_datos_db()

dni_col = 'ID' if 'ID' in df_marc.columns else 'DNI'
df_marc['DNI_STR'] = df_marc[dni_col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
df_marc['Fecha_Clean'] = df_marc['Fecha'].apply(parse_date_val)
df_marc['Hora_Clean'] = df_marc['Tiempo'].apply(parse_time_val)

dni_clean = '48790853'
fecha_next_str = '2026-08-18'

# Test 1: exact match
match1 = df_marc[
    (df_marc['DNI_STR'].apply(lambda d: str(d).strip().lstrip('0')) == dni_clean) &
    (df_marc['Fecha_Clean'] == fecha_next_str)
]
print("Match 1 count:", len(match1))

# Check types of Fecha_Clean
print("Fecha_Clean unique values:", df_marc['Fecha_Clean'].unique())
