import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from core.attendance_engine import procesar_asistencia_df

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

# Ejecutar procesar_asistencia_df
df_asis, df_he, df_inc, _ = procesar_asistencia_df(df_trab, df_marc)

print("=== ASISTENCIA SANGABIL DE PROCESAR_ASISTENCIA_DF ===")
s_asis = df_asis[df_asis['DNI'].astype(str).str.contains('48790853')]
for idx, r in s_asis.iterrows():
    print(dict(r))
