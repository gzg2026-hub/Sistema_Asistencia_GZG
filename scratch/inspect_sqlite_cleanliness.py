import sqlite3

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

print("=== TABLAS EN LA BASE DE DATOS SQLITE (asistencia.db) ===")
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"  - Tabla '{t}': {count} registros")

print("\n--- MUESTRA DE ASISTENCIA DIARIA PROCESADA ---")
cursor.execute("SELECT * FROM asistencia_diaria LIMIT 3")
rows = cursor.fetchall()
col_names = [d[0] for d in cursor.description]
print("Columnas:", col_names)
for r in rows:
    print("  Row:", r)

conn.close()
