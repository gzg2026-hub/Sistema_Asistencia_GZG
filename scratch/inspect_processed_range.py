import sqlite3
import pandas as pd

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)

df_marc = pd.read_sql_query("SELECT COUNT(*) as total_marcaciones FROM marcaciones_raw WHERE fecha >= '2026-08-17';", conn)
print("Total marcaciones raw en DB (>= 2026-08-17):", df_marc.iloc[0]['total_marcaciones'])

df_asis = pd.read_sql_query("SELECT fecha, turno, COUNT(*) as trabajadores FROM asistencia WHERE fecha >= '2026-08-17' GROUP BY fecha, turno ORDER BY fecha, turno;", conn)
print("\n--- RESUMEN DE ASISTENCIA PROCESADA EN BASE DE DATOS (2026-08-17 A 2026-08-20) ---")
print(df_asis.to_string(index=False))

df_juan = pd.read_sql_query("SELECT * FROM asistencia WHERE dni LIKE '%70782038%' AND fecha >= '2026-08-17' ORDER BY fecha;", conn)
print("\n--- DETALLE DE JUAN FERNANDO SANCHEZ MONTERO (70782038) ---")
print(df_juan.to_string(index=False))

conn.close()
