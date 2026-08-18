import os
import time
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--ignore-certificate-errors", "--no-sandbox"]
    )
    context = browser.new_context(ignore_https_errors=True, accept_downloads=True)
    page = context.new_page()

    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded")
    time.sleep(4)

    page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
    page.locator("#username, input[placeholder='Nombre de usuario']").first.fill("admin")
    page.locator("input[type='password']").first.fill("GzG@ACCESO2026")
    page.locator("button:has-text('Iniciar')").first.click()
    time.sleep(5)

    print("Clicking Asistencia using get_by_text...")
    page.get_by_text("Asistencia", exact=True).first.click()
    time.sleep(4)

    print("Clicking Transacciones...")
    page.get_by_text("Transacciones", exact=True).first.click()
    time.sleep(4)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "transacciones_page.png"))
    print("Screenshot saved! URL:", page.url)
    browser.close()
