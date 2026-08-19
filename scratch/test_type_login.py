import sys
import os
import json
import time

from playwright.sync_api import sync_playwright

print("Iniciando prueba keyboard type login...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--no-sandbox"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)

    user_inp = page.locator("#username, input[placeholder='Nombre de usuario']").first
    user_inp.wait_for(state="visible", timeout=15000)

    page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")

    # Focus and type user
    user_inp.click()
    page.keyboard.type("admin", delay=50)

    # Focus and type pass
    pass_inp = page.locator("input[type='password']").first
    pass_inp.click()
    page.keyboard.type("GzG@ACCESO2026", delay=50)

    time.sleep(1)

    login_btn = page.locator("button:has-text('Iniciar'), button:has-text('Log In'), button[type='button']").first
    print("Haciendo clic en el botón de login...", flush=True)
    login_btn.click()
    
    time.sleep(6)
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
    print(f"EXITO TOTAL: {len(records)} marcaciones extraidas.", flush=True)
