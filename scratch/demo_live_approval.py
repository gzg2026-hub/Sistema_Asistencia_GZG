import sys, os, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import actualizar_estado_aprobacion, DB_PATH, get_connection, regenerar_aprobaciones_excel

print("=== PRUEBA DE APROBACION EN VIVO ===")
conn = get_connection(DB_PATH)
row = conn.execute("SELECT id, dni, apellidos, estado_n1, estado FROM aprobaciones WHERE aprobador_n1='jalva' LIMIT 1").fetchone()
conn.close()
print("Antes en BD:", row)

sol_id = row[0]
actualizar_estado_aprobacion(sol_id, 'APROBADO', 'jalva', comentario='Validado por Jhon Alva')

df_excel = pd.read_excel('downloads/data_procesada/Aprobaciones_GZG_2026-08.xlsx', header=3)
r_excel = df_excel[df_excel['DNI'].astype(str).str.contains(str(row[1]))]
print("\nResultado en el Excel local Aprobaciones_GZG_2026-08.xlsx:")
print(r_excel[['DNI', 'Apellidos', 'Fecha Turno', 'Estado Final', 'Aprobador N1', 'Estado N1', 'Comentario Supervisor']].to_string())

conn = get_connection(DB_PATH)
conn.execute("UPDATE aprobaciones SET estado = 'PENDIENTE', estado_n1 = 'PENDIENTE', aprobado_por_n1 = NULL, comentario_n1 = NULL, comentario_supervisor = NULL, fecha_aprobacion = NULL WHERE id = ?", (sol_id,))
conn.commit()
conn.close()
regenerar_aprobaciones_excel(DB_PATH)
print("\n[OK] Excel reseteado limpiamente a PENDIENTE.")
