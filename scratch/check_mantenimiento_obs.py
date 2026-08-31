import os
import sqlite3

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
db_current = os.path.join(PROJECT_ROOT, "data", "asistencia.db")

conn = sqlite3.connect(db_current)
cursor = conn.cursor()

cursor.execute("SELECT fecha, dni, apellidos, nombres, entrada, observaciones FROM asistencia WHERE cargo LIKE '%Mantenimiento%' OR area LIKE '%Mantenimiento%'")
rows = cursor.fetchall()

print(f"Registros de Mantenimiento encontrados: {len(rows)}")
for r in rows:
    print("  ", r)

conn.close()
