import sqlite3

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT id, dni, fecha, tiempo, tipo_pase FROM marcaciones_raw WHERE dni='48790853' ORDER BY fecha, tiempo;")
print("--- MARCACIONES RAW EN ASISTENCIA.DB PARA SANGABIL ---")
for r in cur.fetchall():
    print(r)
