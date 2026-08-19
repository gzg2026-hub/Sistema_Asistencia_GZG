import sqlite3
import os

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Tables in DB ({db_path}): {tables}\n")

    for tbl in tables:
        if tbl == "sqlite_sequence":
            continue
        cur.execute(f"SELECT COUNT(*) FROM {tbl};")
        count = cur.fetchone()[0]
        print(f"--- Table '{tbl}': {count} total rows ---")

        # Check date range if fecha exists
        for col_name in ["fecha", "Fecha", "FECHA"]:
            try:
                cur.execute(f"SELECT MIN({col_name}), MAX({col_name}) FROM {tbl};")
                min_f, max_f = cur.fetchone()
                if min_f or max_f:
                    print(f"  Column '{col_name}' range: {min_f} -> {max_f}")
            except Exception:
                pass
        print()
    conn.close()
else:
    print(f"DB file not found at {db_path}")
