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

    # Clic Asistencia
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Asistencia' && e.offsetHeight > 0);
            if (el) el.click();
        }
    """)
    time.sleep(3)

    # Clic Transacciones
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Transacciones');
            if (el) el.click();
        }
    """)
    time.sleep(3)

    # Clic Exportar
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('button, span, div'))
                .find(e => e.textContent.trim() === 'Exportar');
            if (el) el.click();
        }
    """)
    time.sleep(3)

    # Find inputs inside drawer
    inputs_info = page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('input')).map(i => ({
                placeholder: i.placeholder,
                type: i.type,
                outerHTML: i.outerHTML
            }));
        }
    """)
    print("Inputs in drawer:", inputs_info)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "drawer_opened.png"))
    browser.close()
