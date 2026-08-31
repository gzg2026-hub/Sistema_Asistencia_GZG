import sys, os, sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import actualizar_estado_aprobacion, DB_PATH, get_connection

conn = get_connection(DB_PATH)
row = conn.execute("SELECT id, dni, apellidos, estado, estado_n1, aprobador_n1, aprobador_n2 FROM aprobaciones WHERE aprobador_n1='jalva' LIMIT 1").fetchone()
conn.close()
print("Antes:", row)

if row:
    sol_id = row[0]
    res = actualizar_estado_aprobacion(sol_id, 'APROBADO', 'jalva', comentario='Prueba aprobacion')
    print("Resultado actualizacion:", res)

    conn = get_connection(DB_PATH)
    after = conn.execute("SELECT id, dni, apellidos, estado, estado_n1, estado_n2, aprobado_por, comentario_supervisor, fecha_aprobacion FROM aprobaciones WHERE id = ?", (sol_id,)).fetchone()
    conn.close()
    print("Despues en DB:", after)
