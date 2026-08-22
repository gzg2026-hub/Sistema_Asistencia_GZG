import os
import sys
import time
from playwright.sync_api import sync_playwright

url = "https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
test_file = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\Reporte_Prueba_Conexion_GZG.xlsx"

# Crear un archivo Excel de prueba real
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Prueba Conexion"
ws.append(["DNI", "Apellidos", "Nombres", "Estado Conexión"])
ws.append(["00000000", "PRUEBA", "AUTOMATICA", "EXITOSA - GZG MINERALES 2026"])
wb.save(test_file)
print(f"Archivo Excel de prueba generado en: {test_file}")

user_data_dir = r"C:\Users\GZG Minerales 2026\AppData\Local\Google\Chrome\User Data"

print(f"Abriendo Playwright con perfil de Chrome...")
with sync_playwright() as p:
    try:
        # Intentar conectar con canal chrome o persistent context
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            args=["--remote-debugging-port=9222"]
        )
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        time.sleep(3)
        print(f"Título de la página: {page.title()}")
        
        # Buscar el botón + Nuevo o Drop target para subir archivo
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            print("Cargando archivo vía input[type=file]...")
            file_input.set_input_files(test_file)
            time.sleep(5)
            print("¡Archivo subido exitosamente a Google Drive!")
        else:
            print("Buscando botón + Nuevo...")
            nuevo_btn = page.locator("button:has-text('Nuevo'), div[role='button']:has-text('Nuevo')")
            if nuevo_btn.count() > 0:
                nuevo_btn.first.click()
                time.sleep(1)
                # Escuchar filechooser
                with page.expect_file_chooser() as fc_info:
                    page.click("text=Subir archivo")
                file_chooser = fc_info.value
                file_chooser.set_files(test_file)
                time.sleep(5)
                print("¡Archivo subido a través de FileChooser!")
            else:
                print("No se encontró botón Nuevo directamente.")
        
        browser.close()
    except Exception as e:
        print(f"Error durante la prueba de Playwright: {e}")
