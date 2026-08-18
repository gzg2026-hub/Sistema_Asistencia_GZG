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

    print("Logged in URL:", page.url)

    # Click Asistencia top tab
    asistencia_nav = page.locator("div.header-nav-item:has-text('Asistencia'), div.nav-item:has-text('Asistencia')").first
    asistencia_nav.click()
    time.sleep(4)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "asistencia_tab_clicked.png"))

    # Print all text in left menu
    menu_items = page.locator("ul.el-menu li, div.el-submenu__title, span").all()
    print("Left menu items count:", len(menu_items))
    for idx, item in enumerate(menu_items):
        try:
            t = item.inner_text().strip()
            if t and len(t) < 40:
                print(f"Item {idx}: '{t}'")
        except Exception:
            pass

    browser.close()
