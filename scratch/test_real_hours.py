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

df_asist, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

print("=== BUSCANDO TRABAJADORES CON MARCACIONES TEMPRANAS ===")
for idx, r in df_asist.iterrows():
    ent = str(r.get('ENTRADA', '') or '').strip()
    sal = str(r.get('SALIDA', '') or '').strip()
    if ent and sal and ent not in ('None', 'nan', '') and sal not in ('None', 'nan', ''):
        try:
            h_ent = int(ent.split(':')[0])
            m_ent = int(ent.split(':')[1])
            h_sal = int(sal.split(':')[0])
            m_sal = int(sal.split(':')[1])
            
            if (6 <= h_ent < 7 or 18 <= h_ent < 19) or (h_sal >= 19 and m_sal > 0):
                print(f"DNI: {r.get('DNI')} | {r.get('APELLIDOS')} {r.get('NOMBRES')} | Fecha: {r.get('FECHA')} | Ent: {ent} | Sal: {sal} | Horas Turno: {r.get('HORAS DE TURNO (HH:MM)')} | Exceso: {r.get('EXCESO DE TURNO (HH:MM)')} | Tipo: '{r.get('TIPO_REGISTRO')}' | Obs: '{r.get('INCIDENCIAS')}'")
        except Exception:
            pass

conn.close()
