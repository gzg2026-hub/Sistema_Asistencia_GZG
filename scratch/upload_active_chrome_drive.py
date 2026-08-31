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

print(f"Subiendo {len(files_to_upload)} archivos a Google Drive por navegador...")

with sync_playwright() as p:
    try:
        # Abrir navegador visible para que cargue con la sesión activa
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"Abriendo {folder_url}...")
        page.goto(folder_url, wait_until="domcontentloaded")
        time.sleep(4)

        # Buscar el selector de file input
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            print("Enviando archivos a Google Drive...")
            file_input.first.set_input_files(files_to_upload)
            print("Esperando 10s para finalizar la carga...")
            time.sleep(10)
            print("¡Carga finalizada!")
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\drive_success.png")
        else:
            print(f"Título: {page.title()}")

        browser.close()
    except Exception as e:
        print(f"Aviso en subida: {e}")
