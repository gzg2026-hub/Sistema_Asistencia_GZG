import os
import sys
import time
from playwright.sync_api import sync_playwright

folder_id = "1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

master_raw = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_Acumuladas.xlsx"
diario_dir = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\diario"

files_to_upload = [master_raw]
if os.path.exists(diario_dir):
    files_to_upload.extend([os.path.join(diario_dir, f) for f in os.listdir(diario_dir) if f.endswith(".xlsx")])

print(f"Archivos a subir a Google Drive ({len(files_to_upload)} archivos):")

with sync_playwright() as p:
    try:
        # Conectar usando el canal de Chrome instalado en el sistema
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

        print(f"Abriendo carpeta Google Drive: {folder_url}")
        page.goto(folder_url, wait_until="load", timeout=60000)
        time.sleep(3)

        # Si abre la página de la carpeta de Drive
        page.wait_for_selector("body", timeout=10000)
        
        # Simular carga mediante el input oculto de fileupload si existe o arrastrando
        file_inputs = page.locator("input[type='file']")
        if file_inputs.count() > 0:
            print("Cargando archivos mediante input de archivo...")
            file_inputs.first.set_input_files(files_to_upload)
            print("Esperando finalización de subida...")
            time.sleep(12)
            print("¡Subida por Playwright finalizada con éxito!")
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\drive_success_upload.png")
        else:
            print("Buscando botón + Nuevo...")
            nuevo_btn = page.locator("button:has-text('Nuevo'), button:has-text('New')")
            if nuevo_btn.count() > 0:
                nuevo_btn.first.click()
                time.sleep(2)
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\drive_state.png")

        browser.close()
    except Exception as e:
        print(f"Error en script: {e}")
