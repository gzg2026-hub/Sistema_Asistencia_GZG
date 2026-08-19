import sqlite3

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT DISTINCT fecha, COUNT(*), archivo_origen FROM marcaciones_raw GROUP BY fecha, archivo_origen;")
rows = cur.fetchall()

print("Marcaciones en DB marcaciones_raw:")
for r in rows:
    print(r)

conn.close()
