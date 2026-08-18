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

    print("2. JS Clic en Asistencia...")
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Asistencia' && e.offsetHeight > 0);
            if (el) el.click();
        }
    """)
    time.sleep(4)

    print("3. JS Clic en Transacciones...")
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Transacciones');
            if (el) el.click();
        }
    """)
    time.sleep(4)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "js_click_transacciones.png"))
    print("Page body snippet:", page.locator("body").inner_text()[:400])

    print("4. JS Clic en Exportar...")
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('button, span'))
                .find(e => e.textContent.trim() === 'Exportar');
            if (el) el.click();
        }
    """)
    time.sleep(3)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "js_click_modal.png"))
    browser.close()
