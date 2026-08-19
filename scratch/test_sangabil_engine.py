import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from core.attendance_engine import procesar_asistencia_df

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

sangabil_trab = df_trab[df_trab['DNI'].astype(str).str.contains('48790853')]
sangabil_marc = df_marc[df_marc['ID'].astype(str).str.contains('48790853')]

df_asis, df_he, df_inc, _ = procesar_asistencia_df(sangabil_trab, df_marc)
print("--- ASISTENCIA PROCESADA DE SANGABIL ---")
print(df_asis[['FECHA', 'FECHA_ENTRADA', 'FECHA_SALIDA', 'ENTRADA', 'SALIDA', 'TURNO', 'HORAS TRABAJADAS (HH:MM)', 'EXCESO JORNADA (HH:MM)', 'ESTADO ASISTENCIA']])
