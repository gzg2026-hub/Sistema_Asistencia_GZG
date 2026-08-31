import os
import sys
import time
from playwright.sync_api import sync_playwright

folder_url = "https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
diario_dir = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\diario"
master_raw = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_Acumuladas.xlsx"

files_to_upload = [master_raw]
if os.path.exists(diario_dir):
    files_to_upload.extend([os.path.join(diario_dir, f) for f in os.listdir(diario_dir) if f.endswith(".xlsx")])

print(f"Total archivos a subir: {len(files_to_upload)}")

with sync_playwright() as p:
    try:
        print("Intentando conectar a Chrome vía CDP en puerto 9222...")
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = None
        for p_page in context.pages:
            if "drive.google.com" in p_page.url:
                page = p_page
                print(f"Encontrada pestaña de Google Drive: {page.url}")
                break

        if not page:
            print("Abriendo nueva pestaña de Google Drive...")
            page = context.new_page()
            page.goto(folder_url, wait_until="load")
            time.sleep(3)

        # Buscar el selector de tipo file input
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            print("Subiendo archivos directamente a Google Drive...")
            file_input.first.set_input_files(files_to_upload)
            print("Esperando 10s para finalizar la carga...")
            time.sleep(10)
            print("¡Subida completada con éxito!")
        else:
            print("No se encontró input de archivo en la página activa.")
    except Exception as e:
        print(f"Resultado de conexión CDP: {e}")
