import sys
import os
import json
import time

from playwright.sync_api import sync_playwright

print("Iniciando prueba Vue Element UI login...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--no-sandbox"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded", timeout=15000)
    time.sleep(4)

    page.evaluate("""() => {
        const u = document.querySelector('#username');
        const p = document.querySelector('#password');
        if (u) {
            u.removeAttribute('readonly');
            u.focus();
            u.value = 'admin';
            u.dispatchEvent(new Event('input', { bubbles: true }));
            u.dispatchEvent(new Event('change', { bubbles: true }));
            u.dispatchEvent(new Event('blur', { bubbles: true }));
        }
        if (p) {
            p.removeAttribute('readonly');
            p.focus();
            p.value = 'GzG@ACCESO2026';
            p.dispatchEvent(new Event('input', { bubbles: true }));
            p.dispatchEvent(new Event('change', { bubbles: true }));
            p.dispatchEvent(new Event('blur', { bubbles: true }));
        }
    }""")

    time.sleep(1)

    print("Haciendo clic en .login-btn...", flush=True)
    page.locator(".login-btn").click()

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
