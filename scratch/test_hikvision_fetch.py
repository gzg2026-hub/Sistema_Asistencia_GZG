import sys
import os
import json
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from core.hikvision_downloader import cargar_config_hikvision

cfg = cargar_config_hikvision()
base_url = "https://127.0.0.1"

fecha_inicio = "2026-08-18"
fecha_fin = "2026-08-18"

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--no-sandbox"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    print("Navegando a HikCentral...")
    page.goto(f"{base_url}/#/", wait_until="domcontentloaded")
    time.sleep(3)

    user_inp = page.locator("#username, input[placeholder='Nombre de usuario']").first
    pass_inp = page.locator("input[type='password']").first
    login_btn = page.locator("button:has-text('Iniciar')").first

    if user_inp.count() > 0:
        user_inp.fill("admin")
    if pass_inp.count() > 0:
        pass_inp.fill("GzG@ACCESO2026")

    print("Haciendo clic en login...")
    login_btn.click()
    
    # Esperar a que la URL cambie del login
    try:
        page.wait_for_url(lambda url: "login" not in url.lower() and "#/" in url, timeout=10000)
        print("Login verificado en la URL:", page.url)
    except Exception as e:
        print("Timeout esperando cambio de URL:", e)

    time.sleep(3)

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
    print("Respuesta completa de HikCentral:")
    print(json.dumps(res, indent=2)[:500])
    records = res.get("ResponseStatus", {}).get("Data", {}).get("OriginalRecord", [])
    print(f"\nTotal registros extraídos: {len(records)}")
