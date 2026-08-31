import os
import sys
import time
from playwright.sync_api import sync_playwright

folder_id = "1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
aprob_file = os.path.join(root_dir, "downloads", "data_procesada", "Aprobaciones_GZG_2026-08.xlsx")

if not os.path.exists(aprob_file):
    print("No existe el archivo de aprobaciones local.")
    sys.exit(1)

print(f"Subiendo {aprob_file} a Google Drive...")

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(folder_url, timeout=45000)
        time.sleep(3)
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            file_input.first.set_input_files([aprob_file])
            time.sleep(8)
            print("Subida a Google Drive completada exitosamente vía Playwright!")
        else:
            print(f"Página Drive cargó con título: {page.title()}")
        browser.close()
    except Exception as e:
        print(f"Aviso subida Playwright: {e}")
