import sys
import os
import json
import time

from playwright.sync_api import sync_playwright

print("Iniciando prueba fill login...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--no-sandbox"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded", timeout=15000)
    
    # 1. Esperar a que el campo de usuario sea visible
    user_inp = page.locator("#username, input[placeholder='Nombre de usuario']").first
    user_inp.wait_for(state="visible", timeout=15000)

    # 2. Remover atributo readonly de los inputs
    page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")

    # 3. Llenar usuario y contraseña usando fill
    pass_inp = page.locator("input[type='password']").first
    user_inp.fill("admin")
    pass_inp.fill("GzG@ACCESO2026")

    # 4. Hacer clic en iniciar sesión
    login_btn = page.locator("button:has-text('Iniciar'), button:has-text('Log In'), button[type='button']").first
    login_btn.click()
    
    # 5. Esperar 5 segundos para que la sesión se establezca
    time.sleep(5)
    print("URL post login:", page.url, flush=True)

    payload_js = json.dumps({
        "RecordRequest": {
            "PageIndex": 1,
            "PageSize": 5000,
            "QueryInfo": {
                "SortInfo": { "SortField": 1, "SortType": 1 },
                "BeginTime": "2026-08-18T00:00:00-05:00",
                "EndTime": "2026-08-18T23:59:59-05:00",
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
    print(f"EXITO: {len(records)} marcaciones extraidas.", flush=True)
