import os
import sys
import pandas as pd
import datetime

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import get_connection
from core.attendance_engine import procesar_asistencia_df
from data.exporter import exportar_asistencia_excel

raw_trans = os.path.join(PROJECT_ROOT, "downloads", "data_cruda", "Transacciones_2026-08-17_2026-08-20.xlsx")
df_marc = pd.read_excel(raw_trans)

conn = get_connection(os.path.join(PROJECT_ROOT, "data", "asistencia.db"))
df_trab = pd.read_sql_query("SELECT dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES, cargo as CARGO, area as ÁREA FROM trabajadores", conn)
conn.close()

print(f"Cargados: {len(df_marc)} marcaciones, {len(df_trab)} trabajadores")

df_asist, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

excel_bytes = exportar_asistencia_excel(df_trab, df_marc, df_asist, df_he, df_inc)

ts_str = datetime.datetime.now().strftime("%H%M%S")
out_excel = os.path.join(PROJECT_ROOT, "downloads", "data_procesada", f"Reporte_Asistencia_GZG_2026-08-17_{ts_str}.xlsx")
with open(out_excel, "wb") as f:
    f.write(excel_bytes)

print(f"Reporte procesado guardado con éxito en: {out_excel}")
