"""
ACTUALIZACION COMPLETA DE SISTEMA_ASISTENCIA_GZG_v1.0.xlsx
==========================================================
Procesa el 100% de transacciones acumuladas en downloads/data_cruda/Transacciones_Acumuladas.xlsx
y actualiza el archivo maestro raíz Sistema_Asistencia_GZG_v1.0.xlsx en la PC local.
"""

import os
import sys
import datetime
import sqlite3
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

print("=" * 70)
print("ACTUALIZANDO ARCHIVO PRINCIPAL: Sistema_Asistencia_GZG_v1.0.xlsx")
print(f"Fecha/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

from data.database import (
    DB_PATH,
    init_db,
    sincronizar_padron_desde_excel,
    guardar_asistencia_y_reportes,
    sincronizar_aprobaciones_desde_asistencia,
    get_connection
)
from data.data_loader import parse_hikvision_transaction_file
from core.attendance_engine import procesar_asistencia_df
from data.exporter import exportar_asistencia_excel, exportar_aprobaciones_excel

# 1. Padrón oficial
print("\n1. Sincronizando padrón de trabajadores...")
init_db(DB_PATH)
sincronizar_padron_desde_excel(DB_PATH)

conn = get_connection(DB_PATH)
df_trab = pd.read_sql_query("SELECT dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES, area as AREA, cargo as CARGO FROM trabajadores", conn)
conn.close()
print(f"   Padrón listo: {len(df_trab)} trabajadores.")

# 2. Cargar data cruda
cruda_path = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
if not os.path.exists(cruda_path):
    print(f"ERROR: No se encontró {cruda_path}")
    sys.exit(1)

df_raw = parse_hikvision_transaction_file(cruda_path)
print(f"   Data cruda cargada: {len(df_raw)} marcaciones.")

# 3. Procesar motor de asistencia
print("\n2. Ejecutando motor de cálculo de asistencia...")
df_asist, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_raw)
print(f"   Asistencia diaria calculada: {len(df_asist)} registros.")

# 4. Guardar en SQLite
print("\n3. Actualizando base de datos SQLite (asistencia.db)...")
guardar_asistencia_y_reportes(df_asist, df_he, df_inc, DB_PATH)

# 5. Exportar archivo principal Sistema_Asistencia_GZG_v1.0.xlsx
print("\n4. Generando archivo raíz Sistema_Asistencia_GZG_v1.0.xlsx...")
ruta_root_v1 = os.path.join(ROOT_DIR, "Sistema_Asistencia_GZG_v1.0.xlsx")
excel_bytes = exportar_asistencia_excel(df_trab, df_raw, df_asist, df_he, df_inc)

try:
    with open(ruta_root_v1, "wb") as f_out:
        f_out.write(excel_bytes)
    sz_kb = os.path.getsize(ruta_root_v1) / 1024
    print(f"   [OK] Archivo Sistema_Asistencia_GZG_v1.0.xlsx actualizado con éxito ({sz_kb:.1f} KB).")
except PermissionError:
    print(f"   [AVISO] El archivo 'Sistema_Asistencia_GZG_v1.0.xlsx' está ABIERTO en Excel.")
    print(f"   Cierra Excel en tu PC y vuelve a ejecutar el comando, o guarda una copia.")

# 6. Sincronizar y exportar Aprobaciones del mes
print("\n5. Actualizando Aprobaciones...")
# 1. Rehidratar PRIMERO desde Google Drive para absorber aprobaciones de Streamlit Cloud
try:
    from data.database import sincronizar_aprobaciones_con_gdrive
    sincronizar_aprobaciones_con_gdrive(DB_PATH)
except Exception as e_rehid:
    print(f"   [Aviso rehidratación]: {e_rehid}")

sincronizar_aprobaciones_desde_asistencia(DB_PATH)

conn = get_connection(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    UPDATE aprobaciones
    SET aprobador_n2 = '-'
    WHERE aprobador_n2 IS NULL 
       OR TRIM(LOWER(aprobador_n2)) IN ('', 'none', 'nan')
""")
cursor.execute("""
    UPDATE aprobaciones
    SET estado_n2 = '-'
    WHERE aprobador_n2 = '-'
""")
conn.commit()

df_aprob_final = pd.read_sql_query("SELECT * FROM aprobaciones ORDER BY fecha DESC, id DESC", conn)
conn.close()

mes_str = datetime.date.today().strftime('%Y-%m')
out_aprob = os.path.join(ROOT_DIR, "downloads", "data_procesada", f"Aprobaciones_GZG_{mes_str}.xlsx")
exportar_aprobaciones_excel(df_aprob_final, out_aprob)
print(f"   [OK] Aprobaciones_GZG_{mes_str}.xlsx actualizado ({len(df_aprob_final)} filas acumuladas).")

print("\n" + "=" * 70)
print("ACTUALIZACION COMPLETA REALIZADA EXITOSAMENTE")
print("=" * 70)
