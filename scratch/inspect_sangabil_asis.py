import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from core.attendance_engine import procesar_asistencia_df

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

df_asis, df_he, df_inc, _ = procesar_asistencia_df(df_trab, df_marc)

sangabil_asis = df_asis[df_asis['DNI'].astype(str).str.contains('48790853')]
print("--- ASISTENCIA DE SANGABIL ESPECIFICA ---")
print(sangabil_asis.to_string())
