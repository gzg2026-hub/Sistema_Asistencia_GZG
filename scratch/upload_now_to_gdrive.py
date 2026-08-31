import os
import sys
import time
from playwright.sync_api import sync_playwright

folder_id = "1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

master_raw = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_Acumuladas.xlsx"
diario_dir = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\diario"

# Archivos específicos desde el 17 hasta ayer (21) + Maestro Acumulado
files_to_upload = [master_raw]
if os.path.exists(diario_dir):
    for f in sorted(os.listdir(diario_dir)):
        if f.endswith(".xlsx") and not f.endswith("2026-08-22.xlsx"):
            files_to_upload.append(os.path.join(diario_dir, f))

print(f"=== SUBIENDO {len(files_to_upload)} ARCHIVOS A GOOGLE DRIVE ===")
for f in files_to_upload:
    print(f"  - {os.path.basename(f)}")

with sync_playwright() as p:
    try:
        # Abrir navegador Chromium visible
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"\nNavegando a carpeta Drive: {folder_url}")
        page.goto(folder_url, wait_until="load", timeout=60000)
        time.sleep(4)

        # Buscar el selector de file input
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            print("Iniciando carga masiva a Google Drive...")
            file_input.first.set_input_files(files_to_upload)
            print("Carga enviada. Esperando 12 segundos para completar la sincronización web...")
            time.sleep(12)
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\drive_upload_completed.png")
            print("¡Archivos cargados exitosamente!")
        else:
            print(f"Página cargada con título: {page.title()}")

        browser.close()
    except Exception as e:
        print(f"Error en proceso de subida: {e}")
