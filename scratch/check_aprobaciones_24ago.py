import sqlite3, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.database import get_connection, DB_PATH

conn = get_connection(DB_PATH)

print("=== APROBACIONES POR FECHA ===")
rows = conn.execute(
    "SELECT fecha, COUNT(*) as n FROM aprobaciones GROUP BY fecha ORDER BY fecha DESC"
).fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]} registros")

print()
print("=== REGISTRO 24-AGO ===")
rows24 = conn.execute("SELECT * FROM aprobaciones WHERE fecha = '2026-08-24'").fetchall()
print(f"  Encontrados: {len(rows24)}")

print()
print("=== JALVA - TODAS SUS SOLICITUDES ===")
rows_jalva = conn.execute(
    "SELECT dni, fecha, estado, estado_n1, aprobador_n1 FROM aprobaciones WHERE LOWER(aprobador_n1)='jalva' ORDER BY fecha"
).fetchall()
for r in rows_jalva:
    print(f"  {r}")

print()
print(f"=== TOTAL en DB: {conn.execute('SELECT COUNT(*) FROM aprobaciones').fetchone()[0]} ===")

print()
print("=== INCIDENCIAS TABLA ===")
tablas = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print([t[0] for t in tablas])

# Buscar en incidencias si hay datos del 24
for tabla in [t[0] for t in tablas]:
    if 'incidencia' in tabla.lower() or 'asistencia' in tabla.lower():
        try:
            r = conn.execute(f"SELECT COUNT(*) FROM {tabla} WHERE fecha='2026-08-24'").fetchone()
            print(f"  {tabla} con fecha 24-ago: {r[0]}")
        except:
            pass

conn.close()
