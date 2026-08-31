import os
import sys
import subprocess
import time
from playwright.sync_api import sync_playwright

folder_url = "https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
diario_dir = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\diario"
master_raw = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_Acumuladas.xlsx"

files_to_upload = [master_raw]
if os.path.exists(diario_dir):
    files_to_upload.extend([os.path.join(diario_dir, f) for f in os.listdir(diario_dir) if f.endswith(".xlsx")])

print(f"Total archivos a subir: {len(files_to_upload)}")

# Intentar abrir Chrome con puerto de depuración
try:
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    if os.path.exists(chrome_path):
        cmd = f'"{chrome_path}" --remote-debugging-port=9222'
        subprocess.Popen(cmd, shell=True)
        time.sleep(3)
except Exception as e:
    print(f"Aviso al iniciar Chrome con depuración: {e}")

with sync_playwright() as p:
    try:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.new_page()
        print(f"Abriendo la carpeta de Google Drive: {folder_url}")
        page.goto(folder_url, wait_until="load")
        time.sleep(3)

        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            print("Cargando los archivos directamente...")
            file_input.first.set_input_files(files_to_upload)
            print("Esperando 10 segundos...")
            time.sleep(10)
            print("¡Subida completada!")
            page.screenshot(path=r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\cdp_success.png")
    except Exception as e:
        print(f"Resultado: {e}")
