import openpyxl
import pandas as pd
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file, cargar_datos_excel
from core.attendance_engine import procesar_asistencia_df
from data.database import init_db, guardar_asistencia_y_reportes
from data.exporter import exportar_asistencia_excel, guardar_transacciones_acumuladas_excel
from scripts.gdrive_uploader import subir_archivo_a_gdrive

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")

print("1. Cargando y aplicando formato ejecutivo a Transacciones_Acumuladas.xlsx...")
df_acum = parse_hikvision_transaction_file(ruta_acumuladas)

col_order = [
    'ID', 'Nombre', 'Apellido', 'Departamento', 'Posición',
    'Fecha', 'Semana', 'Tiempo', 'Tipo de pase de tarjeta',
    'Método de verificación', 'Punto de control de asistencia'
]

present_cols = [c for c in col_order if c in df_acum.columns]
other_cols = [c for c in df_acum.columns if c not in col_order]
df_acum_clean = df_acum[present_cols + other_cols]

# Guardar localmente con formato ejecutivo (Azul Corporativo #1F4E78, letras blancas en negrita)
res_acum_local = guardar_transacciones_acumuladas_excel(df_acum_clean, ruta_acumuladas)
print(f"OK: Transacciones_Acumuladas.xlsx guardado localmente con formato corporativo: {res_acum_local}")

print("2. Generando Reporte de Asistencia del 21/08/2026...")
excel_padron = os.path.join(ROOT_DIR, "Padron_Trabajadores_GZG.xlsx")
df_trab, _, _ = cargar_datos_excel(excel_padron)
if df_trab.empty:
    import sqlite3
    conn = sqlite3.connect('data/asistencia.db')
    df_trab = pd.read_sql("SELECT * FROM trabajadores", conn)

df_trab.columns = [c.upper() for c in df_trab.columns]

df_asist, df_inc, df_he, stats = procesar_asistencia_df(df_trab, df_acum_clean)

# Guardar en SQLite
init_db()
guardar_asistencia_y_reportes(df_asist, df_inc, df_he)

# Filtrar solo el día 2026-08-21
df_asist_21 = df_asist[df_asist['FECHA'] == '2026-08-21']
ruta_rep_21 = os.path.join(ROOT_DIR, "downloads", "data_procesada", "diario", "Reporte_Asistencia_GZG_2026-08-21.xlsx")

excel_bytes_21 = exportar_asistencia_excel(df_trab, df_acum_clean, df_asist_21, df_he, df_inc)

with open(ruta_rep_21, "wb") as f:
    f.write(excel_bytes_21)
print(f"OK: Reporte del 21/08 guardado en {ruta_rep_21}")

# Guardar copia temporal en scratch con formato corporativo y subir a Google Drive
temp_acum_path = os.path.join(ROOT_DIR, "scratch", "Transacciones_Acumuladas.xlsx")
guardar_transacciones_acumuladas_excel(df_acum_clean, temp_acum_path)

temp_rep21_path = os.path.join(ROOT_DIR, "scratch", "Reporte_Asistencia_GZG_2026-08-21.xlsx")
with open(temp_rep21_path, "wb") as f:
    f.write(excel_bytes_21)

print("\n3. Subiendo archivos con formato ejecutivo azul corporativo a Google Drive (Carpeta AGOSTO)...")
res_drive1 = subir_archivo_a_gdrive(temp_acum_path, "Transacciones_Acumuladas.xlsx")
print(f"Subida Transacciones_Acumuladas.xlsx: {res_drive1}")

res_drive2 = subir_archivo_a_gdrive(temp_rep21_path, "Reporte_Asistencia_GZG_2026-08-21.xlsx")
print(f"Subida Reporte_Asistencia_GZG_2026-08-21.xlsx: {res_drive2}")

print("PROCESO COMPLETADO Y FORMATO APLICADO EXITOSAMENTE!")
