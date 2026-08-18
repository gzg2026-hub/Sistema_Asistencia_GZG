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
    print("2. Llenando credenciales...")
    user_input = page.locator("input[placeholder='Nombre de usuario']")
    pass_input = page.locator("input[placeholder*='Contrase']")
    login_btn = page.locator("button:has-text('Iniciar')")

    user_input.fill("admin")
    pass_input.fill("GzG@ACCESO2026")
    time.sleep(1)
    login_btn.click()
    print("3. Clic en Iniciar sesión...")

    time.sleep(6)
    print("URL actual:", page.url)

    # Dump menu items
    items = page.locator("li, div.header-nav-item, span").all()
    menu_texts = [it.inner_text().strip() for it in items if it.inner_text().strip()]
    print("Menu elements found:", menu_texts[:30])

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "step4_logged_in.png"))
    browser.close()
