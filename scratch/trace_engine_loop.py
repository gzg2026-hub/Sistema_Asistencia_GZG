import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from core.attendance_engine import parse_date_val, parse_time_val

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

df_marc['DNI_STR'] = df_marc['ID'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
df_marc['Fecha_Clean'] = df_marc['Fecha'].apply(parse_date_val)
df_marc['Hora_Clean'] = df_marc['Tiempo'].apply(parse_time_val)

sangabil_marc = df_marc[df_marc['DNI_STR'].str.contains('48790853')]

grouped = sangabil_marc.groupby(['DNI_STR', 'Fecha_Clean'])
print("Iterando grupos de Sangabil:")
for (dni, fecha), group in grouped:
    print(f"\nGrupo DNI: {dni}, Fecha: {fecha}")
    print(group[['DNI_STR', 'Fecha_Clean', 'Hora_Clean', 'Tipo de pase de tarjeta']])
