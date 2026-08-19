import sqlite3
import os

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\sistema_asistencia.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Tables in DB: {tables}")

    for tbl in tables:
        cur.execute(f"SELECT COUNT(*) FROM {tbl};")
        count = cur.fetchone()[0]
        print(f"  Table '{tbl}': {count} rows")

        # Check date range if Fecha exists
        try:
            cur.execute(f"SELECT MIN(Fecha), MAX(Fecha) FROM {tbl};")
            min_f, max_f = cur.fetchone()
            print(f"    Date range for '{tbl}': {min_f} -> {max_f}")
        except Exception:
            pass
    conn.close()
else:
    print("DB file does not exist.")
