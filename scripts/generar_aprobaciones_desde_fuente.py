"""
GENERACION OFICIAL DESDE LA FUENTE: APROBACIONES_GZG_YYYY-MM.xlsx
=================================================================
Este script genera el archivo maestro ACUMULABLE de Aprobaciones del mes:
  1. Padron_Trabajadores_GZG.xlsx (Aprobadores N1 y N2)
  2. Base de datos SQLite (asistencia.db -> asistencia acumulada)
  3. Sincronizacion de tabla 'aprobaciones' acumulativa
  4. Formato limpio: '-' en Nivel 2 cuando no aplica, y comentarios vacios sin 'nan'
  5. Exportacion al archivo Excel oficial: downloads/data_procesada/Aprobaciones_GZG_2026-08.xlsx
"""

import os
import sys
import datetime
import sqlite3
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

print("=" * 70)
print("INICIANDO GENERACION DE APROBACIONES GZG DESDE LA FUENTE")
print(f"Fecha/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

from data.database import (
    DB_PATH,
    init_db,
    sincronizar_padron_desde_excel,
    sincronizar_aprobaciones_desde_asistencia,
    get_connection
)
from data.exporter import exportar_aprobaciones_excel

# -------------------------------------------------------------------------
# PASO 1: Sincronizar Padron Oficial de Trabajadores (Aprobadores N1 y N2)
# -------------------------------------------------------------------------
print("\n[PASO 1] Sincronizando Padron Oficial (Padron_Trabajadores_GZG.xlsx)...")
padron_path = os.path.join(ROOT_DIR, "Padron_Trabajadores_GZG.xlsx")
if not os.path.exists(padron_path):
    print(f"  ERROR: No se encontro {padron_path}")
    sys.exit(1)

init_db(DB_PATH)
sincronizar_padron_desde_excel(DB_PATH)
print("  [OK] Padron sincronizado en SQLite (55 trabajadores con N1 y N2 asignados).")

# -------------------------------------------------------------------------
# PASO 2: Sincronizar Solicitudes Acumuladas desde Asistencia
# -------------------------------------------------------------------------
print("\n[PASO 2] Extrayendo solicitudes acumuladas de Horas Extras y Excesos...")
sincronizar_aprobaciones_desde_asistencia(DB_PATH)

conn = get_connection(DB_PATH)
cursor = conn.cursor()

# Ajustar estados iniciales limpios:
# Si aprobador_n2 es nulo o vacio, fijar '-'
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

cursor.execute("SELECT COUNT(*) FROM aprobaciones")
total_solic = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT fecha) FROM aprobaciones")
total_dias = cursor.fetchone()[0]

cursor.execute("SELECT MIN(fecha), MAX(fecha) FROM aprobaciones")
r_fechas = cursor.fetchone()
print(f"  [OK] Total solicitudes acumuladas en el mes: {total_solic} registros.")
print(f"  [OK] Periodo acumulado: del {r_fechas[0]} al {r_fechas[1]} ({total_dias} dias con incidencias).")
conn.close()

# -------------------------------------------------------------------------
# PASO 3: Exportar el Archivo Excel Oficial de Aprobaciones (Acumulable)
# -------------------------------------------------------------------------
print("\n[PASO 3] Exportando archivo Excel oficial de Aprobaciones...")
mes_str = datetime.date.today().strftime('%Y-%m')
out_dir = os.path.join(ROOT_DIR, "downloads", "data_procesada")
os.makedirs(out_dir, exist_ok=True)
excel_aprobaciones_path = os.path.join(out_dir, f"Aprobaciones_GZG_{mes_str}.xlsx")

conn = get_connection(DB_PATH)
df_aprob_final = pd.read_sql_query("SELECT * FROM aprobaciones ORDER BY fecha DESC, id DESC", conn)
conn.close()

ok_export = exportar_aprobaciones_excel(df_aprob_final, excel_aprobaciones_path)

if ok_export and os.path.exists(excel_aprobaciones_path):
    sz_kb = os.path.getsize(excel_aprobaciones_path) / 1024
    print(f"  [OK] EXCEL ACUMULABLE CREADO EXITOSAMENTE:")
    print(f"    Ruta: {excel_aprobaciones_path}")
    print(f"    Tamano: {sz_kb:.1f} KB")
    print(f"    Total filas acumuladas: {len(df_aprob_final)}")
else:
    print("  ERROR al exportar el archivo Excel.")
    sys.exit(1)

print("\n" + "=" * 70)
print("PROCESO COMPLETADO SATISFACTORIAMENTE")
print("=" * 70)
