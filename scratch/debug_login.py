import sys
import os
import json
import time

from playwright.sync_api import sync_playwright

print("Iniciando Playwright...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--no-sandbox"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    print("Navegando a https://127.0.0.1/#/...", flush=True)
    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded", timeout=15000)
    print("Pagina cargada. Titulo:", page.title(), flush=True)
    time.sleep(3)

    user_inp = page.locator("#username, input[placeholder='Nombre de usuario'], input[type='text']").first
    pass_inp = page.locator("input[type='password']").first
    login_btn = page.locator("button:has-text('Iniciar'), button:has-text('Log In'), button[type='button']").first

    print("Inputs encontrados - User:", user_inp.count(), "Pass:", pass_inp.count(), "Btn:", login_btn.count(), flush=True)

    if user_inp.count() > 0:
        user_inp.fill("admin")
    if pass_inp.count() > 0:
        pass_inp.fill("GzG@ACCESO2026")

    print("Haciendo clic en login...", flush=True)
    login_btn.click()
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
    print(f"RESULTADO: {len(records)} marcaciones extraidas.", flush=True)
