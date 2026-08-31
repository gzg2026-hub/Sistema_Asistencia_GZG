import sqlite3
import pandas as pd
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

db_path = os.path.join(ROOT_DIR, "data", "asistencia.db")
conn = sqlite3.connect(db_path)

df_asis = pd.read_sql_query("""
SELECT fecha, dni, apellidos, nombres, turno, entrada, salida, horas_trabajadas, estado_asistencia, observaciones
FROM asistencia
WHERE dni = '62772089' AND fecha >= '2026-08-20'
ORDER BY fecha ASC
""", conn)
conn.close()

print("--- EVALUACIÓN DE ASISTENCIA PROCESADA DE JESÚS GABRIEL LADINES AGURTO ---")
print(df_asis.to_string(index=False))
