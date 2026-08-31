import os
import glob
import sqlite3
import datetime
import pandas as pd

ROOT_DIR = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"

import sys
sys.path.insert(0, ROOT_DIR)

from data.database import DB_PATH, get_connection
from data.exporter import exportar_aprobaciones_excel

conn = get_connection(DB_PATH)
cursor = conn.cursor()

# 1. Resetear todas las solicitudes a PENDIENTE y campos de prueba limpios
cursor.execute("""
UPDATE aprobaciones
SET 
    estado = 'PENDIENTE',
    aprobado_por = NULL,
    fecha_aprobacion = NULL,
    comentario_supervisor = '',
    estado_n1 = 'PENDIENTE',
    aprobado_por_n1 = NULL,
    fecha_n1 = NULL,
    comentario_n1 = '',
    estado_n2 = CASE 
        WHEN aprobador_n2 = '-' OR aprobador_n2 IS NULL OR TRIM(LOWER(aprobador_n2)) IN ('', 'none', 'nan') THEN '-' 
        ELSE 'PENDIENTE' 
    END,
    aprobado_por_n2 = NULL,
    fecha_n2 = NULL,
    comentario_n2 = '',
    adjuntos = NULL,
    observacion_trabajador = ''
""")
conn.commit()

cursor.execute("SELECT estado, COUNT(*) FROM aprobaciones GROUP BY estado")
res = cursor.fetchall()
print("Estados en BD tras limpieza:", res)

cursor.execute("SELECT COUNT(*) FROM aprobaciones")
total = cursor.fetchone()[0]
print(f"Total solicitudes restablecidas: {total}")

# 2. Obtener data limpia para exportar Excel
df_aprob = pd.read_sql_query("SELECT * FROM aprobaciones ORDER BY fecha DESC, id DESC", conn)
conn.close()

# 3. Limpiar carpeta de adjuntos de prueba
adj_dir = os.path.join(ROOT_DIR, "downloads", "adjuntos_aprobaciones")
if os.path.exists(adj_dir):
    files = glob.glob(os.path.join(adj_dir, "*"))
    for f in files:
        try:
            os.remove(f)
        except Exception:
            pass
    print(f"Adjuntos limpiados ({len(files)} archivos eliminados).")

# 4. Regenerar Excel de Aprobaciones limpio
mes_str = datetime.date.today().strftime('%Y-%m')
out_path = os.path.join(ROOT_DIR, "downloads", "data_procesada", f"Aprobaciones_GZG_{mes_str}.xlsx")
ok = exportar_aprobaciones_excel(df_aprob, out_path)
if ok:
    print(f"Excel {out_path} generado exitosamente ({len(df_aprob)} filas).")
