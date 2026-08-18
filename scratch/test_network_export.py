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

    # Track network requests
    page.on("request", lambda req: print(f"-> REQUEST: {req.method} {req.url}"))
    page.on("response", lambda res: print(f"<- RESPONSE: {res.status} {res.url}"))

    print("1. Login...")
    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded")
    time.sleep(4)

    page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
    page.locator("#username, input[placeholder='Nombre de usuario']").first.fill("admin")
    page.locator("input[type='password']").first.fill("GzG@ACCESO2026")
    page.locator("button:has-text('Iniciar')").first.click()
    time.sleep(5)

    print("\n--- Navegando a Transacciones ---")
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Asistencia' && e.offsetHeight > 0);
            if (el) el.click();
        }
    """)
    time.sleep(3)

    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Transacciones');
            if (el) el.click();
        }
    """)
    time.sleep(3)

    print("\n--- Clic Exportar ---")
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('button, div, span'))
                .find(e => e.textContent.trim() === 'Exportar');
            if (el) el.click();
        }
    """)
    time.sleep(3)

    print("\n--- Llenar clave y Clic rojo Exportar ---")
    page.evaluate("""
        () => {
            const pwdInp = Array.from(document.querySelectorAll('input[type="password"]')).pop();
            if (pwdInp) {
                pwdInp.focus();
                pwdInp.value = 'GzG@ACCESO2026';
                pwdInp.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    """)
    time.sleep(1)

    page.evaluate("""
        () => {
            const redBtn = Array.from(document.querySelectorAll('button'))
                .find(b => b.textContent.trim() === 'Exportar' && b.offsetHeight > 0 && b.offsetParent !== null);
            if (redBtn) redBtn.click();
        }
    """)
    time.sleep(5)

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "after_export_clicked.png"))
    browser.close()
