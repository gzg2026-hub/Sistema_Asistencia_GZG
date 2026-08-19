import sys
import os
import json
import time

from playwright.sync_api import sync_playwright

base_url = "https://127.0.0.1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--no-sandbox"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.goto(f"{base_url}/#/", wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)

    page.evaluate("""() => {
        const u = document.querySelector('#username');
        const p = document.querySelector('#password');
        if (u && p) {
            u.removeAttribute('readonly'); u.value = 'admin';
            u.dispatchEvent(new Event('input', { bubbles: true }));
            p.removeAttribute('readonly'); p.value = 'GzG@ACCESO2026';
            p.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }""")

    login_btn = page.locator(".login-btn").first
    login_btn.click()
    time.sleep(4)

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
    print("Total registros:", len(records))
    for r in records:
        info = r.get("PersonInfo", {})
        dni = str(info.get("EmployeeID", ""))
        if "44955960" in dni:
            print("\nRaúl Espinoza record:")
            print("  SwipeTime:", r.get("SwipeTime"))
            print("  SwipeType:", r.get("SwipeType"))
            print("  VerifyType:", r.get("VerifyType"))
            print("  AttendancePointName:", r.get("AttendancePointName"))
            print("  Full object keys:", list(r.keys()))
