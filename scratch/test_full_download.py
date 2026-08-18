import os
import time
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads", "hikvision")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--ignore-certificate-errors", "--no-sandbox"]
    )
    context = browser.new_context(ignore_https_errors=True, accept_downloads=True)
    page = context.new_page()

    print("1. Login en HikCentral...")
    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded")
    time.sleep(4)

    page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
    page.locator("#username, input[placeholder='Nombre de usuario']").first.fill("admin")
    page.locator("input[type='password']").first.fill("GzG@ACCESO2026")
    page.locator("button:has-text('Iniciar')").first.click()
    time.sleep(5)

    print("2. Clic en la pestaña Asistencia...")
    asistencia_tab = page.locator("div:has-text('Asistencia'), span:has-text('Asistencia')").first
    asistencia_tab.click()
    time.sleep(3)

    print("3. Clic en Transacciones...")
    trans_item = page.locator("li:has-text('Transacciones'), span:has-text('Transacciones')").first
    trans_item.click()
    time.sleep(3)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "step6_transacciones.png"))

    print("4. Clic en Exportar...")
    export_btn = page.locator("button:has-text('Exportar'), span:has-text('Exportar')").first
    export_btn.click()
    time.sleep(2)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "step7_modal_exportar.png"))

    # Llenar confirmación de contraseña si aparece
    pwd_confirm = page.locator("div.el-dialog input[type='password']")
    if pwd_confirm.count() > 0:
        print("5. Confirmando contraseña en modal...")
        pwd_confirm.first.fill("GzG@ACCESO2026")
        time.sleep(1)

    print("6. Esperando descarga de Excel...")
    with page.expect_download(timeout=20000) as download_info:
        btn_confirm = page.locator("div.el-dialog button:has-text('Exportar'), button.el-button--primary").last
        btn_confirm.click()

    download = download_info.value
    target_path = os.path.join(DOWNLOADS_DIR, "Transacciones_Robot.xlsx")
    download.save_as(target_path)
    print(f"✅ Descarga completada con éxito: {target_path}")

    browser.close()
