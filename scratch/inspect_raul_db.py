import sqlite3
import os

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT id, dni, fecha, tiempo, tipo_pase, metodo_verificacion, archivo_origen FROM marcaciones_raw WHERE dni='44955960';")
for r in cur.fetchall():
    print(r)
