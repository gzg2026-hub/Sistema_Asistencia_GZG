import os
import sys

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from scripts.gdrive_uploader import subir_archivo_a_gdrive

master_raw = os.path.join(PROJECT_ROOT, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
diario_dir = os.path.join(PROJECT_ROOT, "downloads", "data_procesada", "diario")

print("=== VERIFICACION DE INTEGRACION DE SUBIDA A GOOGLE DRIVE ===")
print(f"1. Archivo Maestro Data Cruda: {master_raw}")
if os.path.exists(master_raw):
    print(f"   Existe ({os.path.getsize(master_raw)} bytes)")
    subir_archivo_a_gdrive(master_raw, subfolder_name="Data_Cruda")

print(f"\n2. Archivos Procesados Diarios en: {diario_dir}")
if os.path.exists(diario_dir):
    files = [f for f in os.listdir(diario_dir) if f.endswith(".xlsx")]
    print(f"   Archivos diarios encontrados ({len(files)} archivos):")
    for f in sorted(files):
        p = os.path.join(diario_dir, f)
        print(f"     - {f} ({os.path.getsize(p)} bytes)")
        subir_archivo_a_gdrive(p, subfolder_name="Data_Procesada")
