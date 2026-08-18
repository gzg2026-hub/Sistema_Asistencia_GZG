"""
auto_hikcentral_browser.py
==========================
Robot de automatización de navegador en segundo plano (Playwright)
para descargar automáticamente el Excel de Transacciones desde HikCentral Access Control.
"""

import os
import sys
import time
import datetime
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads", "hikvision")

HIKCENTRAL_URL = "https://127.0.0.1"
USERNAME = "admin"
PASSWORD = "GzG@ACCESO2026"


def ejecutar_descarga_robot(fecha_inicio: str = None, fecha_fin: str = None, headless: bool = True) -> str:
    """
    Abre HikCentral en segundo plano, inicia sesión, va a Asistencia > Transacciones,
    exporta el Excel de las marcaciones y lo guarda en downloads/hikvision/.
    """
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    ayer = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    fecha_inicio = fecha_inicio or ayer
    fecha_fin = fecha_fin or fecha_inicio

    print(f"[Robot-HikCentral] Iniciando descargador automático para fecha: {fecha_inicio} al {fecha_fin}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--ignore-certificate-errors", "--no-sandbox"]
        )
        context = browser.new_context(
            ignore_https_errors=True,
            accept_downloads=True
        )
        page = context.new_page()

        try:
            # 1. Navegar a HikCentral
            print("[Robot-HikCentral] Conectando a HikCentral Access Control...")
            page.goto(f"{HIKCENTRAL_URL}/#/", wait_until="domcontentloaded")
            time.sleep(4)

            # 2. Iniciar sesión si estamos en la pantalla de login
            if "Iniciar" in page.locator("body").inner_text() or page.locator("input[placeholder='Nombre de usuario']").count() > 0:
                print("[Robot-HikCentral] Iniciando sesión con cuenta admin...")
                page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
                time.sleep(1)

                user_input = page.locator("#username, input[placeholder='Nombre de usuario']").first
                pass_input = page.locator("input[type='password']").first
                login_btn = page.locator("button:has-text('Iniciar')").first

                if user_input.count() > 0:
                    user_input.fill(USERNAME)
                if pass_input.count() > 0:
                    pass_input.fill(PASSWORD)

                time.sleep(1)
                login_btn.click()
                print("[Robot-HikCentral] Clic en Iniciar Sesión...")
                time.sleep(5)

            # 3. Cerrar popup "OK" si aparece
            page.evaluate("""
                () => {
                    const okBtn = Array.from(document.querySelectorAll('button, div'))
                        .find(e => e.textContent.trim() === 'OK');
                    if (okBtn) okBtn.click();
                }
            """)
            time.sleep(1)

            # 4. Navegar a pestaña Asistencia
            print("[Robot-HikCentral] Navegando a sección Asistencia...")
            page.evaluate("""
                () => {
                    const el = Array.from(document.querySelectorAll('div, span, li'))
                        .find(e => e.textContent.trim() === 'Asistencia' && e.offsetHeight > 0);
                    if (el) el.click();
                }
            """)
            time.sleep(3)

            # 5. Entrar a Transacciones
            print("[Robot-HikCentral] Navegando a Transacciones...")
            page.evaluate("""
                () => {
                    const el = Array.from(document.querySelectorAll('div, span, li'))
                        .find(e => e.textContent.trim() === 'Transacciones');
                    if (el) el.click();
                }
            """)
            time.sleep(3)

            # Cerrar cualquier aviso OK adicional
            page.evaluate("""
                () => {
                    const okBtn = Array.from(document.querySelectorAll('button, div, span'))
                        .find(e => e.textContent.trim() === 'OK');
                    if (okBtn) okBtn.click();
                }
            """)
            time.sleep(1)

            # 6. Clic en Exportar
            print("[Robot-HikCentral] Abriendo ventana de Exportar...")
            page.evaluate("""
                () => {
                    const el = Array.from(document.querySelectorAll('button, span, div'))
                        .find(e => e.textContent.trim().includes('Exportar'));
                    if (el) el.click();
                }
            """)
            time.sleep(3)

            # 7. Llenar contraseña en el panel de Configuración a exportar
            print("[Robot-HikCentral] Llenando contraseña de confirmación...")
            drawer_pwd = page.locator("div.el-drawer input[type='password'], input[placeholder*='Contraseña']").last
            drawer_pwd.evaluate("el => el.removeAttribute('readonly')")
            drawer_pwd.click()
            drawer_pwd.fill(PASSWORD)
            time.sleep(1)

            # 8. Clic en botón rojo Exportar y guardar la descarga
            target_filename = f"Transacciones_{fecha_inicio}_{fecha_fin}.xlsx"
            target_path = os.path.join(DOWNLOADS_DIR, target_filename)

            print("[Robot-HikCentral] Confirmando Exportación y descargando Excel...")
            with page.expect_download(timeout=30000) as download_info:
                export_confirm_btn = page.locator("div.el-drawer button:has-text('Exportar'), button.el-button--danger:has-text('Exportar')").first
                export_confirm_btn.click()

            download = download_info.value
            download.save_as(target_path)
            print(f"[Robot-HikCentral] ✅ EXCEL DESCARGADO CON ÉXITO EN: {target_path}")
            browser.close()
            return target_path

        except Exception as e:
            print(f"[Robot-HikCentral] Error durante autodescarga: {e}")
            try:
                screenshot_path = os.path.join(PROJECT_ROOT, "scratch", "robot_error.png")
                page.screenshot(path=screenshot_path)
                print(f"[Robot-HikCentral] Captura de depuración guardada en: {screenshot_path}")
            except Exception:
                pass
            browser.close()

    return ""


if __name__ == "__main__":
    is_headless = "--visible" not in sys.argv
    path = ejecutar_descarga_robot(headless=is_headless)
    if path and os.path.exists(path):
        print(f"Descarga finalizada. Tamaño del archivo: {os.path.getsize(path)} bytes")
