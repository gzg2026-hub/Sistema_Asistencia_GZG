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

    print("2. Clic Asistencia...")
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Asistencia' && e.offsetHeight > 0);
            if (el) el.click();
        }
    """)
    time.sleep(3)

    print("3. Clic Transacciones...")
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Transacciones');
            if (el) el.click();
        }
    """)
    time.sleep(3)

    print("4. Clic Exportar (abrir panel)...")
    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('button, span, div'))
                .find(e => e.textContent.trim() === 'Exportar');
            if (el) el.click();
        }
    """)
    time.sleep(3)

    print("5. Llenar clave y hacer clic en Exportar rojo...")
    # Fill any password input if present
    page.evaluate("""
        () => {
            const pwd = document.querySelector('div.el-drawer input[type="password"]');
            if (pwd) {
                pwd.removeAttribute('readonly');
                pwd.value = 'GzG@ACCESO2026';
                pwd.dispatchEvent(new Event('input', { bubbles: true }));
                pwd.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    """)
    time.sleep(1)

    print("6. Esperando descarga...")
    with page.expect_download(timeout=25000) as download_info:
        page.evaluate("""
            () => {
                const btns = Array.from(document.querySelectorAll('button'));
                const exportBtn = btns.find(b => b.textContent.trim() === 'Exportar' && (b.className.includes('danger') || b.className.includes('primary')));
                if (exportBtn) {
                    exportBtn.click();
                } else {
                    const lastExport = btns.filter(b => b.textContent.trim() === 'Exportar').pop();
                    if (lastExport) lastExport.click();
                }
            }
        """)

    download = download_info.value
    target_path = os.path.join(DOWNLOADS_DIR, "Transacciones_Robot_Final.xlsx")
    download.save_as(target_path)
    print(f"🎉 EXCEL DESCARGADO CON ÉXITO: {target_path}")
    print(f"Tamaño: {os.path.getsize(target_path)} bytes")

    browser.close()
