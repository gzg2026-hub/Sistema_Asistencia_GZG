import sqlite3

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== DETALLES DE LA ESTRUCTURA SQLITE ===")
tables = ['trabajadores', 'marcaciones_raw', 'asistencia', 'horas_extra', 'incidencias']

for t in tables:
    cursor.execute(f"PRAGMA table_info({t})")
    cols = [c[1] for c in cursor.fetchall()]
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"\n[Tabla] '{t}' ({count} registros):")
    print("   Columnas:", cols)
    cursor.execute(f"SELECT * FROM {t} LIMIT 1")
    row = cursor.fetchone()
    if row:
        print("   Ejemplo:", row)

conn.close()
