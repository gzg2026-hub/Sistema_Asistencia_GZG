import sqlite3, pandas as pd, datetime, os
import sys

ROOT_DIR = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, ROOT_DIR)

from data.database import DB_PATH, get_connection
from data.exporter import exportar_aprobaciones_excel
from scripts.gdrive_uploader import subir_archivo_a_gdrive

conn = get_connection(DB_PATH)
cursor = conn.cursor()

# Limpiar entrada y salida cuando son nulas o nan
cursor.execute("""
    UPDATE aprobaciones
    SET entrada = '-'
    WHERE entrada IS NULL OR TRIM(LOWER(entrada)) IN ('', 'nan', 'none');
""")
cursor.execute("""
    UPDATE aprobaciones
    SET salida = '-'
    WHERE salida IS NULL OR TRIM(LOWER(salida)) IN ('', 'nan', 'none');
""")
# Para Juan Silva en 2026-08-24 especificamente: entrada y salida de turno ordinario son '-'
cursor.execute("""
    UPDATE aprobaciones
    SET entrada = '-', salida = '-'
    WHERE dni = '41090274' AND fecha = '2026-08-24';
""")
conn.commit()

df_aprob = pd.read_sql_query("SELECT * FROM aprobaciones ORDER BY fecha DESC, id DESC", conn)
conn.close()

mes_str = datetime.date.today().strftime('%Y-%m')
out_path = os.path.join(ROOT_DIR, "downloads", "data_procesada", f"Aprobaciones_GZG_{mes_str}.xlsx")
exportar_aprobaciones_excel(df_aprob, out_path)
print(f"Exportado {out_path} ({len(df_aprob)} filas).")

ok_drive = subir_archivo_a_gdrive(out_path)
print(f"Subida a Google Drive: {ok_drive}")
