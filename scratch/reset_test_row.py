import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.database import get_connection, DB_PATH, regenerar_aprobaciones_excel

conn = get_connection(DB_PATH)
conn.execute("""
    UPDATE aprobaciones
    SET estado = 'PENDIENTE',
        estado_n1 = 'PENDIENTE',
        estado_n2 = 'PENDIENTE',
        aprobado_por = NULL,
        aprobado_por_n1 = NULL,
        aprobado_por_n2 = NULL,
        comentario_supervisor = NULL,
        comentario_n1 = NULL,
        comentario_n2 = NULL,
        fecha_aprobacion = NULL,
        fecha_n1 = NULL,
        fecha_n2 = NULL
    WHERE id = 1173
""")
conn.commit()
conn.close()

regenerar_aprobaciones_excel(DB_PATH)
print("Row 1173 reset to PENDIENTE successfully!")
