import openpyxl
import pandas as pd
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file, cargar_datos_excel
from core.attendance_engine import procesar_asistencia_df
from data.database import init_db, guardar_asistencia_y_reportes
from data.exporter import exportar_asistencia_excel

print("1. Cargando padron y acumuladas...")
ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
excel_padron = os.path.join(ROOT_DIR, "Padron_Trabajadores_GZG.xlsx")

df_trab, _, _ = cargar_datos_excel(excel_padron)
if df_trab.empty:
    import sqlite3
    conn = sqlite3.connect('data/asistencia.db')
    df_trab = pd.read_sql("SELECT * FROM trabajadores", conn)

df_trab.columns = [c.upper() for c in df_trab.columns]
df_acum = parse_hikvision_transaction_file(ruta_acumuladas)

col_order = [
    'ID', 'Nombre', 'Apellido', 'Departamento', 'Posición',
    'Fecha', 'Semana', 'Tiempo', 'Tipo de pase de tarjeta',
    'Método de verificación', 'Punto de control de asistencia'
]

present_cols = [c for c in col_order if c in df_acum.columns]
other_cols = [c for c in df_acum.columns if c not in col_order]
df_acum_clean = df_acum[present_cols + other_cols]

print("2. Procesando asistencia corregida para todo el personal...")
df_asist, df_inc, df_he, stats = procesar_asistencia_df(df_trab, df_acum_clean)

# Guardar en DB SQLite
init_db()
guardar_asistencia_y_reportes(df_asist, df_inc, df_he)

# 3. Generar ÚNICAMENTE el reporte local principal Sistema_Asistencia_GZG_v1.0.xlsx en la raiz de la PC
ruta_v1 = os.path.join(ROOT_DIR, "Sistema_Asistencia_GZG_v1.0.xlsx")
excel_bytes_v1 = exportar_asistencia_excel(df_trab, df_acum_clean, df_asist, df_he, df_inc)

with open(ruta_v1, "wb") as f_out:
    f_out.write(excel_bytes_v1)

print(f"OK Guardado exitosamente EN LA PC LOCAL: Sistema_Asistencia_GZG_v1.0.xlsx (Sin subir a Google Drive)")
