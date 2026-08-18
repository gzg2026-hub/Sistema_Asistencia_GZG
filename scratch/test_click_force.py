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

    print("1. Force clicking Asistencia...")
    page.locator("div[title='Asistencia'], span:has-text('Asistencia')").first.click(force=True)
    time.sleep(3)

    print("2. Force clicking Transacciones...")
    page.locator("li:has-text('Transacciones'), span:has-text('Transacciones')").first.click(force=True)
    time.sleep(3)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "transacciones_page_forced.png"))
    print("Screenshot saved! URL:", page.url)

    # Print visible body text
    print("Body text preview:", page.locator("body").inner_text()[:400])

    browser.close()
