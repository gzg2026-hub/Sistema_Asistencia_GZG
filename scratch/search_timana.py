import os
import sqlite3
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
db_current = os.path.join(PROJECT_ROOT, "data", "asistencia.db")

conn = sqlite3.connect(db_current)
cursor = conn.cursor()

cursor.execute("SELECT * FROM trabajadores WHERE apellidos LIKE '%TIMAN%' OR nombres LIKE '%ANDERSON%' OR dni LIKE '%7529566%'")
res = cursor.fetchall()
print("Búsqueda de Timana Navarro en trabajadores:")
print(res)

conn.close()
