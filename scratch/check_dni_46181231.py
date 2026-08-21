import os
import sys
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import get_connection

conn = get_connection(os.path.join(PROJECT_ROOT, "data", "asistencia.db"))
df_trab = pd.read_sql_query("SELECT * FROM trabajadores WHERE dni LIKE '%46181231%'", conn)
print("=== TRABAJADOR 46181231 EN SQLITE ===")
print(df_trab.to_string(index=False))

df_all = pd.read_sql_query("SELECT count(*) as total FROM trabajadores", conn)
print(f"\nTotal Trabajadores en SQLite DB: {df_all['total'].iloc[0]}")
conn.close()
