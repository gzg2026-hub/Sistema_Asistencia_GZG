import sqlite3, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.database import get_connection, DB_PATH

conn = get_connection(DB_PATH)

print("=== VERIFICAR APROBADORES DE LOS 44 REGISTROS ===")
rows = conn.execute("""
    SELECT a.fecha, a.dni, a.aprobador_n1, a.aprobador_n2, t.aprobador_n1 as t_n1, t.aprobador_n2 as t_n2
    FROM aprobaciones a
    LEFT JOIN trabajadores t ON a.dni = t.dni
    ORDER BY a.fecha, a.dni
""").fetchall()

sin_n1 = [r for r in rows if not r[2] or str(r[2]).strip().lower() in ('none', 'nan', '')]
print(f"Total aprobaciones: {len(rows)}")
print(f"Sin aprobador_n1 asignado: {len(sin_n1)}")
print("\nRegistros sin N1:")
for r in sin_n1:
    print(f"  fecha={r[0]}, dni={r[1]}, ap_n1={r[2]}, t_n1={r[4]}, t_n2={r[5]}")

print("\n=== JALVA N1 CON APROBADORES ===")
jalva_rows = conn.execute("""
    SELECT a.fecha, a.dni, a.aprobador_n1, a.aprobador_n2
    FROM aprobaciones a
    WHERE LOWER(TRIM(COALESCE(a.aprobador_n1,''))) = 'jalva'
    ORDER BY a.fecha
""").fetchall()
for r in jalva_rows: print(" ", r)
print(f"Total jalva N1: {len(jalva_rows)}")

conn.close()
