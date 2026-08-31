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

print("1. Cargando padron y marcaciones de acumuladas...")
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

# 2. Procesar asistencia con el motor corregido
print("2. Procesando asistencia con la regla corregida de Juan Fernando...")
df_asist, df_inc, df_he, stats = procesar_asistencia_df(df_trab, df_acum_clean)

# Guardar en SQLite DB
init_db()
guardar_asistencia_y_reportes(df_asist, df_inc, df_he)

# 3. Re-generar reportes diarios (17/08 al 22/08)
fechas_disponibles = sorted([f for f in df_asist['FECHA'].dropna().unique() if str(f).startswith('2026')])
print(f"3. Generando reportes diarios para fechas: {fechas_disponibles}")

dir_diario = os.path.join(ROOT_DIR, "downloads", "data_procesada", "diario")
os.makedirs(dir_diario, exist_ok=True)

for f_str in fechas_disponibles:
    df_f = df_asist[df_asist['FECHA'] == f_str]
    excel_bytes = exportar_asistencia_excel(df_trab, df_acum_clean, df_f, df_he, df_inc)
    
    rep_name = f"Reporte_Asistencia_GZG_{f_str}.xlsx"
    rep_path = os.path.join(dir_diario, rep_name)
    
    try:
        with open(rep_path, "wb") as f_out:
            f_out.write(excel_bytes)
        print(f"OK Guardado localmente: {rep_name}")
    except Exception as e:
        print(f"Aviso guardando localmente {rep_name}: {e}")
        
    # Copia a scratch y subida a Google Drive
    temp_path = os.path.join(ROOT_DIR, "scratch", rep_name)
    with open(temp_path, "wb") as f_out:
        f_out.write(excel_bytes)
    res_drive = subir_archivo_a_gdrive(temp_path, rep_name)
    print(f"Subida a Google Drive {rep_name}: {res_drive}")

# 4. Generar reporte consolidado completo
rep_cons_name = "Reporte_Asistencia_Procesado_2026-08-17_2026-08-23.xlsx"
excel_bytes_cons = exportar_asistencia_excel(df_trab, df_acum_clean, df_asist, df_he, df_inc)
rep_cons_path = os.path.join(ROOT_DIR, rep_cons_name)

try:
    with open(rep_cons_path, "wb") as f_out:
        f_out.write(excel_bytes_cons)
    print(f"OK Guardado consolidado raiz: {rep_cons_name}")
except Exception as e:
    print(f"Aviso guardando consolidado raiz: {e}")

temp_cons_path = os.path.join(ROOT_DIR, "scratch", rep_cons_name)
with open(temp_cons_path, "wb") as f_out:
    f_out.write(excel_bytes_cons)
res_drive_cons = subir_archivo_a_gdrive(temp_cons_path, rep_cons_name)
print(f"Subida a Google Drive {rep_cons_name}: {res_drive_cons}")

print("\nRE-GENERACIÓN Y SINCRONIZACIÓN DE TODOS LOS REPORTES COMPLETADA!")
