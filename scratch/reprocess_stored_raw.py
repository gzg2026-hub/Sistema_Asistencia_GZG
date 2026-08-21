import os
import sys
import datetime
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import get_connection, guardar_asistencia_y_reportes
from core.attendance_engine import procesar_asistencia_df
from data.exporter import exportar_asistencia_excel

raw_dir = os.path.join(PROJECT_ROOT, "downloads", "data_cruda")
raw_files = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith(".xlsx") and not f.startswith("~$")]

# Encontrar el archivo crudo más reciente que tenga datos
valid_raw_file = None
for rf in sorted(raw_files, key=os.path.getmtime, reverse=True):
    df_temp = pd.read_excel(rf)
    if len(df_temp) > 50:
        valid_raw_file = rf
        break

print(f"=== REPROCESANDO ASISTENCIA CON ARCHIVO ENCONTRADO ===")
print(f"Archivo crudo utilizado: {valid_raw_file}")

df_marc = pd.read_excel(valid_raw_file)

db_path = os.path.join(PROJECT_ROOT, "data", "asistencia.db")
conn = get_connection(db_path)
df_trab = pd.read_sql_query("SELECT dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES, cargo as CARGO, area as ÁREA FROM trabajadores", conn)

print(f"Cargados: {len(df_marc)} marcaciones crudas, {len(df_trab)} trabajadores")

# Procesar Asistencia
df_asist, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

guardar_asistencia_y_reportes(df_asist, df_he, df_inc, db_path)

excel_bytes = exportar_asistencia_excel(df_trab, df_marc, df_asist, df_he, df_inc)

fecha_inicio = "2026-08-17"
fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
ts_str = datetime.datetime.now().strftime("%H%M%S")

carpeta_proc = os.path.join(PROJECT_ROOT, "downloads", "data_procesada")
proc_excel_path = os.path.join(carpeta_proc, f"Reporte_Asistencia_GZG_{fecha_inicio}_al_{fecha_hoy}_{ts_str}.xlsx")
with open(proc_excel_path, "wb") as f:
    f.write(excel_bytes)

conn.close()

print(f"=== PROCESAMIENTO COMPLETADO EXITOSAMENTE ===")
print(f"Filas de asistencia procesadas: {len(df_asist)}")
print(f"Reporte procesado guardado en: {proc_excel_path}")
