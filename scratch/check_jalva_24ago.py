import sqlite3, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.database import get_connection, DB_PATH

conn = get_connection(DB_PATH)

print("=== JALVA N1 ===")
rows = conn.execute(
    "SELECT dni, fecha, estado, estado_n1, aprobador_n1, aprobador_n2 FROM aprobaciones WHERE LOWER(TRIM(aprobador_n1))='jalva' ORDER BY fecha"
).fetchall()
for r in rows: print(" ", r)

print("=== JALVA N2 ===")
rows2 = conn.execute(
    "SELECT dni, fecha, estado, estado_n1, aprobador_n1, aprobador_n2 FROM aprobaciones WHERE LOWER(TRIM(aprobador_n2))='jalva' ORDER BY fecha"
).fetchall()
for r in rows2: print(" ", r)

print("=== 24-AGO DETALLE ===")
rows24 = conn.execute(
    "SELECT dni, fecha, aprobador_n1, aprobador_n2 FROM aprobaciones WHERE fecha='2026-08-24'"
).fetchall()
for r in rows24: print(" ", r)

conn.close()
