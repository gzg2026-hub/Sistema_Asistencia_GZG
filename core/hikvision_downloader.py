"""
hikvision_downloader.py
=======================
Módulo de descarga de transacciones desde HikCentral Access Control / biométricos Hikvision.
Utiliza automatización en segundo plano para extraer directamente las marcaciones de HikCentral.
"""

import os
import json
import time
import datetime
import urllib3
from typing import Optional
from openpyxl import Workbook

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ASISTENCIA_DIR = os.path.join(PROJECT_ROOT, "downloads", "hikvision")


def cargar_config_hikvision():
    """Lee la configuración de IP y credenciales desde config_hikvision.json si existe."""
    config_file = os.path.join(PROJECT_ROOT, "config_hikvision.json")
    defaults = {
        "host": "127.0.0.1",
        "port": 443,
        "scheme": "https",
        "username": "admin",
        "password": "GzG@ACCESO2026"
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults


def descargar_transacciones_hikvision(
    carpeta_destino: str = DEFAULT_ASISTENCIA_DIR,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> str:
    """
    Extrae automáticamente las marcaciones de transacciones desde HikCentral Access Control V2.4
    utilizando Playwright en segundo plano y las guarda en formato Excel oficial de HikCentral.
    """
    cfg = cargar_config_hikvision()
    host = host or cfg.get("host", "127.0.0.1")
    port = port or cfg.get("port", 443)
    scheme = cfg.get("scheme", "https")
    username = username or cfg.get("username", "admin")
    password = password or cfg.get("password", "GzG@ACCESO2026")

    os.makedirs(carpeta_destino, exist_ok=True)

    ayer = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    if not fecha_inicio:
        fecha_inicio = ayer
    if not fecha_fin:
        fecha_fin = fecha_inicio

    filename = f"Transacciones_{fecha_inicio}_{fecha_fin}.xlsx"
    target_path = os.path.join(carpeta_destino, filename)

    base_url = f"{scheme}://{host}:{port}" if port not in (80, 443) else f"{scheme}://{host}"

    print(f"[HikCentral] Extrayendo transacciones del {fecha_inicio} al {fecha_fin}...")
    print(f"[HikCentral] Servidor: {base_url} | Usuario: {username}")

    records = []

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--ignore-certificate-errors", "--no-sandbox"]
            )
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            page.goto(f"{base_url}/#/", wait_until="domcontentloaded")
            time.sleep(4)

            page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
            user_inp = page.locator("#username, input[placeholder='Nombre de usuario']").first
            pass_inp = page.locator("input[type='password']").first
            login_btn = page.locator("button:has-text('Iniciar')").first

            if user_inp.count() > 0:
                user_inp.fill(username)
            if pass_inp.count() > 0:
                pass_inp.fill(password)

            login_btn.click()
            time.sleep(5)

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
            records = res.get("ResponseStatus", {}).get("Data", {}).get("OriginalRecord", [])
            print(f"[HikCentral] Autenticación exitosa. {len(records)} marcaciones extraídas.")

    except Exception as e:
        print(f"[HikCentral] Error durante autodescarga: {e}")

    # Generar Excel en el formato oficial de HikCentral que reconoce data_loader.py
    wb = Workbook()
    ws = wb.active
    ws.title = "Transacciones"

    # Fila 1: Título / Periodo
    ws.append([f"Periodo : {fecha_inicio} - {fecha_fin}", "", "", "", "", "", "", "", "", ""])

    # Fila 2: Encabezados oficiales de HikCentral
    ws.append([
        "ID", "Nombre", "Apellido", "Cargo", "Departamento",
        "Grupo de asistencia", "Tiempo", "Tipo de pase de tarjeta",
        "Método de verificación", "Punto de control de asistencia"
    ])

    for r in records:
        info = r.get("PersonInfo", {})
        dni = str(info.get("EmployeeID", ""))
        nombre = info.get("GivenName", "")
        apellido = info.get("FamilyName", "")
        cargo = info.get("Post", "")
        dept = info.get("DepartmentName", "")
        grupo = info.get("AttGroupName", "")

        swipe_time = r.get("SwipeTime", "")  # "2026-08-18T07:06:30-05:00"
        fecha_ev = swipe_time[:10] if len(swipe_time) >= 10 else fecha_inicio
        hora_ev = swipe_time[11:19] if len(swipe_time) >= 19 else "00:00:00"
        tiempo_str = f"{fecha_ev} {hora_ev}"

        tipo_pase = "Registro de entrada" if r.get("SwipeType") == 1 else "Registrar salida" if r.get("SwipeType") == 2 else "Marcación"
        metodo = "Huella dactilar" if r.get("VerifyType") == 2 else "Rostro" if r.get("VerifyType") == 1 else "Tarjeta"
        punto = r.get("AttendancePointName", "")

        ws.append([dni, nombre, apellido, cargo, dept, grupo, tiempo_str, tipo_pase, metodo, punto])

    try:
        wb.save(target_path)
    except PermissionError:
        ts = datetime.datetime.now().strftime("%H%M%S")
        target_path = os.path.join(carpeta_destino, f"Transacciones_{fecha_inicio}_{fecha_fin}_{ts}.xlsx")
        wb.save(target_path)
        print(f"[HikCentral] Archivo en uso, guardado como: {target_path}")

    print(f"[HikCentral] Archivo guardado con éxito en: {target_path}")
    return target_path
