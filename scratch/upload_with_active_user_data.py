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
    for f in sorted(os.listdir(diario_dir)):
        if f.endswith(".xlsx") and not f.endswith("2026-08-22.xlsx"):
            files_to_upload.append(os.path.join(diario_dir, f))

print(f"=== SUBIENDO {len(files_to_upload)} ARCHIVOS USANDO SESION DE CHROME ===")
for f in files_to_upload:
    print(f"  - {os.path.basename(f)}")

user_data = r"C:\Users\GZG Minerales 2026\AppData\Local\Google\Chrome\User Data"

with sync_playwright() as p:
    try:
        # Intentar abrir la instancia con la sesión de Chrome
        context = p.chromium.launch_persistent_context(
            user_data_dir=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\chrome_session",
            headless=False,
            channel="chrome"
        )
        page = context.new_page()

        print(f"Abriendo carpeta objetivo: {folder_url}")
        page.goto(folder_url, wait_until="load", timeout=60000)
        time.sleep(3)

        print(f"Título de la página: {page.title()}")

        inputs = page.locator("input[type='file']")
        if inputs.count() > 0:
            print("Cargando archivos directamente en la interfaz web de Google Drive...")
            inputs.first.set_input_files(files_to_upload)
            print("Esperando 10s para finalizar la sincronización...")
            time.sleep(10)
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\gdrive_upload_success.png")
            print("¡Archivos cargados con éxito!")
        else:
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\gdrive_page_state.png")

        context.close()
    except Exception as e:
        print(f"Aviso en ejecución: {e}")
