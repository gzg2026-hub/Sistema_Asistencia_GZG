import sqlite3

conn = sqlite3.connect('data/asistencia.db')
cursor = conn.cursor()

# Actualizar el rol de admin a ADMINISTRADOR
cursor.execute("UPDATE usuarios SET rol = 'ADMINISTRADOR' WHERE username = 'admin'")
conn.commit()

print("--- TABLA USUARIOS ACTUALIZADA ---")
cursor.execute("SELECT id, username, nombre_completo, rol, area_asignada, cargo FROM usuarios")
for r in cursor.fetchall():
    print(r)

conn.close()
