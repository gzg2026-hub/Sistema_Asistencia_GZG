import os
import sys
import shutil
import time
from playwright.sync_api import sync_playwright

url = "https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
test_file = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\Reporte_Prueba_Conexion_GZG.xlsx"

# Crear Excel de prueba
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Prueba GZG"
ws.append(["DNI", "Apellidos", "Nombres", "Estado Conexión"])
ws.append(["00000000", "PRUEBA", "AUTOMATICA", "CONEXION DRIVE EXITOSA - GZG MINERALES 2026"])
wb.save(test_file)

# Copiar perfil de Chrome a un temp dir para evitar bloqueo de archivo si Chrome está abierto
orig_dir = r"C:\Users\GZG Minerales 2026\AppData\Local\Google\Chrome\User Data"
temp_dir = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\chrome_temp_profile"

if not os.path.exists(temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    # Copiar Default profile essential files
    src_default = os.path.join(orig_dir, "Default")
    dst_default = os.path.join(temp_dir, "Default")
    if os.path.exists(src_default):
        try:
            shutil.copytree(src_default, dst_default, ignore=shutil.ignore_patterns('Cache*', 'Code Cache*', 'GPUCache*'))
        except Exception as e:
            print(f"Aviso copia perfil: {e}")

print("Iniciando navegador Playwright con sesión de usuario...")
with sync_playwright() as p:
    try:
        context = p.chromium.launch_persistent_context(
            user_data_dir=temp_dir,
            headless=False,
            channel="chrome"
        )
        page = context.new_page()
        print(f"Navegando a la carpeta de Google Drive...")
        page.goto(url, wait_until="load", timeout=60000)
        time.sleep(5)
        
        # Verificar si cargó la página de Google Drive
        page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\gdrive_page.png")
        print(f"Captura guardada. Título: {page.title()}")
        
        # Subir archivo usando filechooser o drag-and-drop / input file
        # En Google Drive, habitualmente hay un input type=file en la página o al activar Nuevo -> Subir archivo
        try:
            with page.expect_file_chooser(timeout=5000) as fc_info:
                # Click en el botón + Nuevo
                page.click("button:has-text('Nuevo'), div[role='button']:has-text('Nuevo')", timeout=5000)
                time.sleep(1)
                page.click("text=Subir archivo", timeout=5000)
            fc = fc_info.value
            fc.set_files(test_file)
            print("Cargando archivo mediante FileChooser...")
            time.sleep(8)
            print("¡Carga completada!")
        except Exception as e_fc:
            print(f"Intento 1 FileChooser: {e_fc}")
            # Intento 2: set_input_files directo
            inputs = page.locator("input[type='file']")
            if inputs.count() > 0:
                inputs.first.set_input_files(test_file)
                time.sleep(8)
                print("¡Carga completada mediante input[type=file]!")
        
        context.close()
    except Exception as e:
        print(f"Error en Playwright: {e}")
