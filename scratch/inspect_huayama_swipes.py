import os
import sys
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import get_connection
from core.attendance_engine import procesar_asistencia_df

raw_dir = os.path.join(PROJECT_ROOT, "downloads", "data_cruda")
raw_files = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith(".xlsx") and not f.startswith("~$")]

valid_raw_file = sorted(raw_files, key=os.path.getmtime, reverse=True)[0]
df_marc = pd.read_excel(valid_raw_file)
db_path = os.path.join(PROJECT_ROOT, "data", "asistencia.db")
conn = get_connection(db_path)
df_trab = pd.read_sql_query("SELECT dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES, cargo as CARGO, area as ÁREA FROM trabajadores", conn)

dni_target = "46671923"
print(f"=== MARCACIONES CRUDAS PARA DNI {dni_target} ===")
col_dni = [c for c in df_marc.columns if 'ID' in c or 'DNI' in c or 'Persona' in c or 'n' in c.lower()][0]
marc_huayama = df_marc[df_marc[col_dni].astype(str).str.strip().str.replace(r'\.0$', '', regex=True) == dni_target]
print(marc_huayama.to_string())

print(f"\n=== PROCESAMIENTO COMPLETO ===")
df_asist, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)
asist_huayama = df_asist[df_asist['DNI'].astype(str).str.strip() == dni_target]
print(asist_huayama[['FECHA', 'DNI', 'NOMBRES', 'ENTRADA', 'SALIDA', 'HORAS DE TURNO (HH:MM)', 'EXCESO DE TURNO (HH:MM)', 'HORAS EXTRAS (HH:MM)', 'TOTAL DE HORAS ADICIONALES (HH:MM)', 'TIPO_REGISTRO', 'INCIDENCIAS']].to_string())

conn.close()
