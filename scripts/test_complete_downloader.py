import os
import json
import time
import datetime
from playwright.sync_api import sync_playwright
from openpyxl import Workbook

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, "downloads", "hikvision")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def descargar_transacciones_playwright(fecha_inicio: str = None, fecha_fin: str = None) -> str:
    ayer = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    fecha_inicio = fecha_inicio or ayer
    fecha_fin = fecha_fin or fecha_inicio

    filename = f"Transacciones_{fecha_inicio}_{fecha_fin}.xlsx"
    target_path = os.path.join(DOWNLOADS_DIR, filename)

    print(f"[HikCentral-Robot] Extrayendo marcaciones del {fecha_inicio} al {fecha_fin}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--ignore-certificate-errors", "--no-sandbox"]
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded")
        time.sleep(4)

        page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
        page.locator("#username, input[placeholder='Nombre de usuario']").first.fill("admin")
        page.locator("input[type='password']").first.fill("GzG@ACCESO2026")
        page.locator("button:has-text('Iniciar')").first.click()
        time.sleep(5)

        # Consultar API nativa de HikCentral desde el navegador autenticado
        payload_js = json.dumps({
            "RecordRequest": {
                "PageIndex": 1,
                "PageSize": 5000,
                "QueryInfo": {
                    "SortInfo": { "SortField": 1, "SortType": 1 },
                    "BeginTime": f"{fecha_inicio}T00:00:00-05:00",
                    "EndTime": f"{fecha_fin}T23:59:59-05:00",
                    "PersonID": [],
                    "PersonCustomFiledID": [],
                    "RecordType": 1
                }
            }
        })

        res = page.evaluate(f"""
            async () => {{
                const resp = await fetch('/ISAPI/Bumblebee/AttendancePlugin/V1/Record?MT=GET', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                    }},
                    body: JSON.stringify({payload_js})
                }});
                return await resp.json();
            }}
        """)

        browser.close()

    # Procesar registros
    records = res.get("ResponseStatus", {}).get("Data", {}).get("OriginalRecord", [])
    print(f"[HikCentral-Robot] {len(records)} marcaciones extraídas desde HikCentral.")

    # Guardar Excel compatible con GZG
    wb = Workbook()
    ws = wb.active
    ws.title = "Transacciones"
    ws.append(["DNI", "APELLIDOS", "NOMBRES", "FECHA", "HORA", "DISPOSITIVO", "TIPO"])

    for r in records:
        info = r.get("PersonInfo", {})
        dni = str(info.get("EmployeeID", ""))
        apellidos = info.get("FamilyName", "")
        nombres = info.get("GivenName", "")

        swipe_time = r.get("SwipeTime", "")  # "2026-08-18T07:06:30-05:00"
        fecha = swipe_time[:10] if len(swipe_time) >= 10 else ""
        hora = swipe_time[11:19] if len(swipe_time) >= 19 else ""
        dispositivo = r.get("AttendancePointName", "")
        tipo = "Marcación"

        ws.append([dni, apellidos, nombres, fecha, hora, dispositivo, tipo])

    try:
        wb.save(target_path)
    except PermissionError:
        ts = datetime.datetime.now().strftime("%H%M%S")
        target_path = os.path.join(DOWNLOADS_DIR, f"Transacciones_{fecha_inicio}_{fecha_fin}_{ts}.xlsx")
        wb.save(target_path)

    print(f"[HikCentral-Robot] Archivo Excel guardado en: {target_path}")
    return target_path

if __name__ == "__main__":
    descargar_transacciones_playwright("2026-08-17", "2026-08-18")
