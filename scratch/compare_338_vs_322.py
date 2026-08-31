import os
import sqlite3

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
db_current = os.path.join(PROJECT_ROOT, "data", "asistencia.db")
db_backup = os.path.join(PROJECT_ROOT, "data", "asistencia_backup.db")

print("=== COMPARACIÓN DETALLADA 338 VS 322 REGISTROS ===")

if os.path.exists(db_backup):
    conn_b = sqlite3.connect(db_backup)
    cur_b = conn_b.cursor()
    cur_b.execute("SELECT fecha, COUNT(*) FROM asistencia GROUP BY fecha")
    print("Fechas en Backup (338 filas):", cur_b.fetchall())
    
    cur_b.execute("SELECT DISTINCT dni FROM asistencia WHERE dni NOT IN (SELECT dni FROM trabajadores)")
    dnis_extra = cur_b.fetchall()
    print("DNIs en backup que no estaban en trabajadores:", dnis_extra)
    conn_b.close()

conn_c = sqlite3.connect(db_current)
cur_c = conn_c.cursor()
cur_c.execute("SELECT fecha, COUNT(*) FROM asistencia GROUP BY fecha")
print("\nFechas en Actual (322 filas):", cur_c.fetchall())
conn_c.close()
