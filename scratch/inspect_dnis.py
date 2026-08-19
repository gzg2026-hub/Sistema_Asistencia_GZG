import sqlite3
import os

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- BUSCANDO EN TABLA TRABAJADORES ---")
cur.execute("SELECT dni, apellidos, nombres FROM trabajadores WHERE dni LIKE '%3208053%' OR dni LIKE '%6616501%' OR apellidos LIKE '%MORETO%' OR apellidos LIKE '%ORDOÑEZ%' OR apellidos LIKE '%ORDONEZ%';")
for r in cur.fetchall():
    print("Trabajador:", repr(r[0]), r[1], r[2])

print("\n--- BUSCANDO EN TABLA MARCACIONES_RAW ---")
cur.execute("SELECT DISTINCT dni, nombre, apellido FROM marcaciones_raw WHERE dni LIKE '%3208053%' OR dni LIKE '%6616501%' OR apellido LIKE '%MORETO%' OR apellido LIKE '%ORDOÑEZ%' OR apellido LIKE '%ORDONEZ%';")
for r in cur.fetchall():
    print("Marcacion Raw:", repr(r[0]), r[1], r[2])
