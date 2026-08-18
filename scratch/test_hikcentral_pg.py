import os
import sys

# Try importing psycopg2 or sqlite or pg8000 or asyncpg
try:
    import psycopg2
except ImportError:
    os.system(f'"{sys.executable}" -m pip install psycopg2-binary')
    import psycopg2

passwords = ["Hik12345", "Hik12345+", "hik12345", "hik12345+", "postgres", "root", "GzG@ACCESO2026"]
users = ["postgres", "hcp", "root"]
databases = ["postgres", "hcp", "vsm", "acs", "event_db", "bms"]

print("Probando conexión directa a PostgreSQL de HikCentral (127.0.0.1:5432)...")

connected = False
for pwd in passwords:
    for usr in users:
        for db in databases:
            try:
                conn = psycopg2.connect(
                    host="127.0.0.1",
                    port=5432,
                    user=usr,
                    password=pwd,
                    dbname=db,
                    connect_timeout=2
                )
                print(f"\n[ÉXITO] Conectado a PostgreSQL HikCentral!")
                print(f"  Usuario: {usr} | Database: {db} | Password: {pwd}")
                
                cur = conn.cursor()
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
                tables = [r[0] for r in cur.fetchall()]
                print(f"  Tablas encontradas ({len(tables)}): {tables[:20]}")
                conn.close()
                connected = True
                break
            except Exception:
                continue
        if connected:
            break
    if connected:
        break

if not connected:
    print("No se pudo adivinar la clave por defecto de Postgres. Probando inspección de config...")
