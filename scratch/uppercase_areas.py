import sqlite3

conn = sqlite3.connect('data/asistencia.db')
cursor = conn.cursor()

# 1. Poner en MAYÚSCULAS area_asignada en la tabla usuarios
cursor.execute("UPDATE usuarios SET area_asignada = UPPER(area_asignada)")

# 2. Asegurar que las áreas en usuarios sean exactamente las correctas en mayúsculas
cursor.execute("UPDATE usuarios SET area_asignada = 'OPER&MTTO' WHERE username IN ('jagreda', 'jhuayama')")
cursor.execute("UPDATE usuarios SET area_asignada = 'JEFATURA' WHERE username IN ('jalva', 'jdelariva', 'msanchez')")
cursor.execute("UPDATE usuarios SET area_asignada = 'TODAS' WHERE username = 'admin'")

conn.commit()

print("--- TABLA USUARIOS ACTUALIZADA (ÁREAS EN MAYÚSCULAS) ---")
cursor.execute("SELECT id, username, nombre_completo, rol, area_asignada, cargo FROM usuarios")
for r in cursor.fetchall():
    print(r)

conn.close()
