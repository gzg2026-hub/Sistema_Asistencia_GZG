import os
import sqlite3
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
db_current = os.path.join(PROJECT_ROOT, "data", "asistencia.db")
db_backup = os.path.join(PROJECT_ROOT, "data", "asistencia_backup.db")

print("=== VERIFICACIÓN DETALLADA DE DNIs Y ASISTENCIA ===")

conn = sqlite3.connect(db_current)

# 1. Verificar a Yenkli y Franco en asistencia actual
cursor = conn.cursor()
cursor.execute("SELECT fecha, dni, apellidos, nombres, entrada, salida, estado_asistencia FROM asistencia WHERE dni LIKE '%6616501%' OR dni LIKE '%3208053%' OR apellidos LIKE '%ORDO%NEZ%' OR apellidos LIKE '%MORETO%'")
rows_yf = cursor.fetchall()
print("\n[OK] Asistencias actuales de Yenkli Ordonez y Franco Moreto en asistencia.db:")
for r in rows_yf:
    print("  ", r)

# 2. Investigar DNIs 41090271 y 75295662 en backup y marcaciones_raw
print("\n[OK] Investigando a quienes pertenecen los DNIs 41090271 y 75295662:")

cursor.execute("SELECT DISTINCT dni, nombre, apellido, cargo, departamento FROM marcaciones_raw WHERE dni IN ('41090271', '75295662') OR dni LIKE '%41090271%' OR dni LIKE '%75295662%'")
raw_owners = cursor.fetchall()
print("  Marcaciones Raw:", raw_owners)

if os.path.exists(db_backup):
    conn_b = sqlite3.connect(db_backup)
    cur_b = conn_b.cursor()
    cur_b.execute("SELECT DISTINCT dni, apellidos, nombres, cargo, area FROM asistencia WHERE dni IN ('41090271', '75295662')")
    backup_owners = cur_b.fetchall()
    print("  Backup Asistencia:", backup_owners)
    conn_b.close()

conn.close()
