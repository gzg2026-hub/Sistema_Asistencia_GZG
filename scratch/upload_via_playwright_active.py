import os
import time
from playwright.sync_api import sync_playwright

url = "https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
test_file = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\Reporte_Prueba_Conexion_GZG.xlsx"

# Crear archivo de prueba
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Prueba GZG"
ws.append(["DNI", "Apellidos", "Nombres", "Estado Conexión"])
ws.append(["00000000", "PRUEBA", "AUTOMATICA", "CONEXION DRIVE EXITOSA - GZG MINERALES 2026"])
wb.save(test_file)

print(f"Probando carga a Google Drive en: {url}")

with sync_playwright() as p:
    # Usar chromium independiente
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    print("Navegando a la URL del Drive...")
    page.goto(url)
    time.sleep(4)
    page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\drive_screen_1.png")
    print(f"Página abierta: {page.title()}")
    browser.close()
