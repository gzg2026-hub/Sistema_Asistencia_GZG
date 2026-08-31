import os
import sqlite3
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
db_current = os.path.join(PROJECT_ROOT, "data", "asistencia.db")

conn = sqlite3.connect(db_current)
cursor = conn.cursor()

cursor.execute("SELECT * FROM trabajadores WHERE dni IN ('41090271', '75295662') OR apellidos LIKE '%SILVA%' OR apellidos LIKE '%TIMANA%'")
res = cursor.fetchall()
print("Búsqueda de Silva y Timana en tabla trabajadores de asistencia.db:")
print(res)

conn.close()
