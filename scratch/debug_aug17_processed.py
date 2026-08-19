import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from core.attendance_engine import procesar_asistencia_df

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db("2026-08-17", "2026-08-18")

df_asis, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

print("--- REGISTROS PROCESADOS DE ASISTENCIA DÍA 2026-08-17 ---")
df_17 = df_asis[df_asis['FECHA'] == '2026-08-17']
print(df_17[['FECHA', 'DNI', 'APELLIDOS', 'ENTRADA', 'SALIDA', 'ESTADO ASISTENCIA']].head(30))
