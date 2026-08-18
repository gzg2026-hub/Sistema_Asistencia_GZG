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

    print("1. Navegando a HikCentral...")
    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded")
    time.sleep(4)

    # 2. Login
    print("2. Removiendo readonly y llenando credenciales...")
    page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
    time.sleep(1)

    user_input = page.locator("#username, input[placeholder='Nombre de usuario']").first
    pass_input = page.locator("input[type='password']").first
    login_btn = page.locator("button:has-text('Iniciar')").first

    user_input.click()
    user_input.fill("admin")

    pass_input.click()
    pass_input.fill("GzG@ACCESO2026")
    time.sleep(1)

    login_btn.click()
    print("3. Clic en Iniciar sesión...")

    time.sleep(6)
    print("URL actual:", page.url)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "step5_after_login.png"))
    browser.close()
