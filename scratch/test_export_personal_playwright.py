import os
import sys
import time
import datetime
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads", "data_cruda")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

HIKCENTRAL_URL = "https://127.0.0.1"
USERNAME = "admin"
PASSWORD = "GzG@ACCESO2026"

print("[Test-Personal] Iniciando automatización para descargar información de personas...")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--ignore-certificate-errors", "--no-sandbox"]
    )
    context = browser.new_context(
        ignore_https_errors=True,
        accept_downloads=True
    )
    page = context.new_page()

    try:
        # 1. Navegar a HikCentral
        print("[1] Conectando a HikCentral...")
        page.goto(f"{HIKCENTRAL_URL}/#/", wait_until="domcontentloaded")
        time.sleep(3)

        # 2. Login
        if page.locator("input[placeholder='Nombre de usuario']").count() > 0 or "Iniciar" in page.locator("body").inner_text():
            print("[2] Iniciando sesión...")
            page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
            time.sleep(1)
            page.locator("#username, input[placeholder='Nombre de usuario']").first.fill(USERNAME)
            page.locator("input[type='password']").first.fill(PASSWORD)
            page.locator("button:has-text('Iniciar')").first.click()
            time.sleep(4)

        # 3. Cerrar emergentes OK
        page.evaluate("""
            () => {
                const okBtn = Array.from(document.querySelectorAll('button, div'))
                    .find(e => e.textContent.trim() === 'OK');
                if (okBtn) okBtn.click();
            }
        """)
        time.sleep(1)

        # 4. Ir a Persona
        print("[3] Navegando a módulo 'Persona'...")
        page.evaluate("""
            () => {
                const el = Array.from(document.querySelectorAll('div, span, li, a'))
                    .find(e => e.textContent.trim() === 'Persona' && e.offsetHeight > 0);
                if (el) el.click();
            }
        """)
        time.sleep(3)

        # 5. Clic en 'Exportar'
        print("[4] Buscando botón 'Exportar'...")
        page.evaluate("""
            () => {
                const expBtn = Array.from(document.querySelectorAll('button, div, span, i'))
                    .find(e => e.textContent.trim().includes('Exportar') && e.offsetHeight > 0);
                if (expBtn) expBtn.click();
            }
        """)
        time.sleep(2)

        # 6. Clic en el botón rojo 'Exportar' dentro del modal/panel lateral
        print("[5] Clic en el botón Exportar dentro del panel lateral...")
        downloadcenter_dir = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter"
        files_before = set(os.listdir(downloadcenter_dir)) if os.path.exists(downloadcenter_dir) else set()

        page.evaluate("""
            () => {
                const btns = Array.from(document.querySelectorAll('button'));
                const redBtn = btns.find(b => (b.textContent.trim() === 'Exportar' || b.className.includes('el-button--danger') || b.className.includes('primary')) && b.offsetHeight > 0);
                if (redBtn) {
                    redBtn.click();
                } else {
                    const lastExp = btns.filter(b => b.textContent.trim() === 'Exportar').pop();
                    if (lastExp) lastExp.click();
                }
            }
        """)
        print("[6] Clic realizado. Esperando que el servidor guarde en Downloadcenter...")
        
        # Esperar 5-10 segundos a que aparezca el nuevo archivo en Downloadcenter
        new_file = None
        for _ in range(12):
            time.sleep(1)
            files_after = set(os.listdir(downloadcenter_dir)) if os.path.exists(downloadcenter_dir) else set()
            added = files_after - files_before
            if added:
                new_file = list(added)[0]
                print(f"[SUCCESS] Nuevo archivo/carpeta detectado en Downloadcenter: {new_file}")
                break

    except Exception as e:
        print("[ERROR] Ocurrió una excepción:", e)
    finally:
        browser.close()
