import sys
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import obtener_trabajadores_master, obtener_datos_db, guardar_asistencia_y_reportes
from core.attendance_engine import procesar_asistencia_df

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

df_asis, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

print(f"Marcaciones evaluadas: {len(df_marc)}")
print(f"Asistencia filas: {len(df_asis)}")
print(f"Horas extra filas: {len(df_he)}")
print(f"Incidencias filas: {len(df_inc)}")

if not df_inc.empty:
    print("\nMuestra de incidencias generadas:")
    print(df_inc.head())
    
    # Guardar en SQLite si no está vacía
    guardar_asistencia_y_reportes(df_asis, df_he, df_inc)
    print("✔ Incidencias oficiales guardadas en SQLite asistencia.db")
