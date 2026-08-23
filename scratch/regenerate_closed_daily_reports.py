import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file
from data.database import guardar_trabajadores, guardar_asistencia_y_reportes, obtener_trabajadores_master
from core.attendance_engine import procesar_asistencia_df
from data.exporter import exportar_asistencia_excel, guardar_excel_base
from scripts.gdrive_uploader import subir_archivo_a_gdrive

print("=== PROCESAMIENTO REGENERATIVO DE DÍAS CERRADOS (17 AL 21 DE AGOSTO) ===")

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
df_marc_master = parse_hikvision_transaction_file(ruta_acumuladas)

# 1. Obtener lista de trabajadores de la base de datos
df_trab = obtener_trabajadores_master()

print(f"Total marcaciones cargadas de Transacciones_Acumuladas.xlsx: {len(df_marc_master)}")
print(f"Total trabajadores en maestro: {len(df_trab)}")

# 2. Procesar asistencia con el motor inteligente
df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc_master)

# 3. Guardar en base de datos SQLite local
guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)

# 4. Actualizar localmente el archivo raíz principal en la PC (SIN subir a Drive)
ruta_root_v1 = os.path.join(ROOT_DIR, "Sistema_Asistencia_GZG_v1.0.xlsx")
excel_bytes_root = exportar_asistencia_excel(df_trab, df_marc_master, df_asis, df_he_out, df_inc)
with open(ruta_root_v1, "wb") as f_out:
    f_out.write(excel_bytes_root)
print(f"Archivo local actualizado en PC: {ruta_root_v1}")

# 5. Generar Reportes Diarios Procesados SOLO para días cerrados 17, 18, 19, 20 y 21 de Agosto
carp_diario = os.path.join(ROOT_DIR, "downloads", "data_procesada", "diario")
os.makedirs(carp_diario, exist_ok=True)

dias_cerrados = ["2026-08-17", "2026-08-18", "2026-08-19", "2026-08-20", "2026-08-21"]

reportes_generados = []

for f_dia in dias_cerrados:
    df_asis_dia = df_asis[df_asis['FECHA'].astype(str) == f_dia]
    if not df_asis_dia.empty:
        file_name_dia = f"Reporte_Asistencia_GZG_{f_dia}.xlsx"
        file_path_dia = os.path.join(carp_diario, file_name_dia)

        excel_bytes = exportar_asistencia_excel(df_trab, df_marc_master, df_asis_dia, df_he_out, df_inc)
        with open(file_path_dia, "wb") as f_out:
            f_out.write(excel_bytes)
        
        reportes_generados.append(file_path_dia)
        print(f"Generado reporte diario local: {file_name_dia} ({len(df_asis_dia)} registros de asistencia)")

# 6. Finalizado estrictamente local en PC
print("\n=== PROCESO COMPLETADO CON ÉXITO LOCALMENTE EN PC (SIN TOCAR GOOGLE DRIVE) ===")
