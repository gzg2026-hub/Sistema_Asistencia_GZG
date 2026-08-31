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

# Intentar Playwright conectándose a Chrome con remote debugging o perfil persistente aislado
user_data_dir = r"C:\Users\GZG Minerales 2026\AppData\Local\Google\Chrome\User Data"
temp_profile = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\gdrive_profile"

if not os.path.exists(temp_profile):
    os.makedirs(temp_profile, exist_ok=True)

with sync_playwright() as p:
    try:
        # Abrir navegador con perfil de Chrome
        browser = p.chromium.launch_persistent_context(
            user_data_dir=temp_profile,
            headless=False,
            channel="chrome"
        )
        page = browser.new_page()
        print(f"Navegando a Google Drive: {folder_url}")
        page.goto(folder_url, wait_until="load", timeout=60000)
        time.sleep(4)
        print(f"Título obtenido: {page.title()}")
        
        # Verificar si requiere inicio de sesión
        if "inicio de sesión" in page.title().lower() or "sign in" in page.title().lower() or "login" in page.title().lower():
            print("AVISO: Google Drive requiere inicio de sesión en este perfil navegante.")
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\gdrive_login_needed.png")
        else:
            # Buscar inputs de tipo archivo en Google Drive
            inputs = page.locator("input[type='file']")
            print(f"Inputs de archivo encontrados: {inputs.count()}")
            if inputs.count() > 0:
                for f_path in files_to_upload:
                    if os.path.exists(f_path):
                        print(f"Subiendo: {os.path.basename(f_path)}...")
                        inputs.first.set_input_files(f_path)
                        time.sleep(3)
                print("¡Carga completada!")
                page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\gdrive_success.png")

        browser.close()
    except Exception as e:
        print(f"Error en script de carga: {e}")
