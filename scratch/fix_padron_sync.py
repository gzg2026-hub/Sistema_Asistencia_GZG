import sqlite3, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.database import get_connection, DB_PATH, sincronizar_padron_desde_excel

# Verificar tabla trabajadores
conn = get_connection(DB_PATH)
total_t = conn.execute("SELECT COUNT(*) FROM trabajadores").fetchone()[0]
print(f"Trabajadores en DB: {total_t}")

if total_t > 0:
    rows = conn.execute("SELECT dni, apellidos, aprobador_n1, aprobador_n2 FROM trabajadores ORDER BY dni LIMIT 10").fetchall()
    print("Muestra:")
    for r in rows: print(" ", r)
conn.close()

# Re-sincronizar el padrón
print("\nRe-sincronizando padron...")
sincronizar_padron_desde_excel(DB_PATH)

conn = get_connection(DB_PATH)
total_t2 = conn.execute("SELECT COUNT(*) FROM trabajadores").fetchone()[0]
print(f"Trabajadores en DB despues: {total_t2}")

# Ver DNIs en trabajadores vs aprobaciones
dnis_aprobaciones = {r[0] for r in conn.execute("SELECT DISTINCT dni FROM aprobaciones").fetchall()}
dnis_trabajadores = {r[0] for r in conn.execute("SELECT DISTINCT dni FROM trabajadores").fetchall()}
no_match = dnis_aprobaciones - dnis_trabajadores
print(f"\nDNIs en aprobaciones sin match en trabajadores ({len(no_match)}):")
for d in sorted(no_match): print(f"  {d}")
conn.close()
