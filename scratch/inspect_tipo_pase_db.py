import sqlite3
import os

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT DISTINCT tipo_pase, COUNT(*) FROM marcaciones_raw GROUP BY tipo_pase;")
print("--- DISTRIBUCION DE TIPO_PASE EN DB ---")
for r in cur.fetchall():
    print(r)
