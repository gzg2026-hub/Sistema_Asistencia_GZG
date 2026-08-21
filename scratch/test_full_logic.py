import os
import sys
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import get_connection
from core.attendance_engine import procesar_asistencia_df

conn = get_connection(os.path.join(PROJECT_ROOT, "data", "asistencia.db"))
df_trab = pd.read_sql_query("SELECT dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES, cargo as CARGO, area as ÁREA FROM trabajadores", conn)
conn.close()

raw_path = os.path.join(PROJECT_ROOT, "downloads", "data_cruda", "Transacciones_2026-08-17_2026-08-20.xlsx")
df_marc = pd.read_excel(raw_path)

print(f"Trabajadores: {len(df_trab)}, Marcaciones: {len(df_marc)}")
