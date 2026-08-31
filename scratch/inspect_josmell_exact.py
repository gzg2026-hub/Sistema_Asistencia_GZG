import os
import sqlite3

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
db_current = os.path.join(PROJECT_ROOT, "data", "asistencia.db")

conn = sqlite3.connect(db_current)
cursor = conn.cursor()

cursor.execute("SELECT * FROM trabajadores WHERE apellidos LIKE '%HUAYAMA%' OR nombres LIKE '%JOSMELL%' OR dni LIKE '%46671923%'")
rows = cursor.fetchall()

print("=== REGISTRO DE JOSMELL EN TABLA TRABAJADORES ===")
for r in rows:
    print(" ", r)

cursor.execute("SELECT DISTINCT dni, nombre, apellido, cargo, departamento FROM marcaciones_raw WHERE dni LIKE '%46671923%' OR apellido LIKE '%HUAYAMA%'")
raw_rows = cursor.fetchall()
print("\n=== REGISTRO DE JOSMELL EN MARCACIONES_RAW ===")
for r in raw_rows:
    print(" ", r)

conn.close()
