import sqlite3

conn = sqlite3.connect('data/asistencia.db')
cursor = conn.cursor()

# Actualizar usuario jagreda a JEFE
cursor.execute("""
UPDATE usuarios 
SET rol = 'JEFE',
    cargo = 'Jefe',
    area_asignada = 'Oper&Mtto'
WHERE username = 'jagreda'
""")

# Actualizar trabajador 47783594 a Jefe
cursor.execute("""
UPDATE trabajadores
SET cargo = 'Jefe',
    area = 'Oper&Mtto'
WHERE dni = '47783594'
""")

# Actualizar en asistencia y aprobaciones
cursor.execute("""
UPDATE asistencia
SET cargo = 'Jefe',
    area = 'Oper&Mtto'
WHERE dni = '47783594'
""")

cursor.execute("""
UPDATE aprobaciones
SET cargo = 'Jefe',
    area = 'Oper&Mtto'
WHERE dni = '47783594'
""")

conn.commit()

print("--- TABLA USUARIOS ACTUALIZADA ---")
cursor.execute("SELECT id, username, nombre_completo, rol, area_asignada, cargo FROM usuarios")
for r in cursor.fetchall():
    print(r)

print("\n--- TRABAJADOR 47783594 ---")
cursor.execute("SELECT dni, nombres, apellidos, cargo, area, aprobador_n1, aprobador_n2 FROM trabajadores WHERE dni = '47783594'")
print(cursor.fetchone())

conn.close()
