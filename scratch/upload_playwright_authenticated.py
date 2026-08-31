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
for f in files_to_upload:
    print(f"  - {os.path.basename(f)}")

with sync_playwright() as p:
    try:
        # Intentar conectar a Chrome que ya tiene la sesión abierta
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print(f"Navegando a la carpeta de Google Drive: {folder_url}")
        page.goto(folder_url, wait_until="networkidle", timeout=60000)
        time.sleep(3)

        # Buscar el selector de subida
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            print("Cargando archivos directamente en la página web...")
            file_input.first.set_input_files(files_to_upload)
            print("Archivos cargados en el formulario web. Esperando 10s para finalizar subida...")
            time.sleep(10)
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\drive_upload_finished.png")
            print("¡Subida completada exitosamente!")
        else:
            print("No se encontró elemento de subida directo.")

        browser.close()
    except Exception as e:
        print(f"Error durante la subida por Playwright: {e}")
