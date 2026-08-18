import os
import json
import time
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

    print("Fetching records directly via page.evaluate(fetch)...")
    res = page.evaluate("""
        async () => {
            const resp = await fetch('/ISAPI/Bumblebee/AttendancePlugin/V1/Record?MT=GET', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                },
                body: JSON.stringify({
                    RecordRequest: {
                        PageIndex: 1,
                        PageSize: 2000,
                        QueryInfo: {
                            SortInfo: { SortField: 1, SortType: 1 },
                            BeginTime: "2026-08-01T00:00:00-05:00",
                            EndTime: "2026-08-31T23:59:59-05:00",
                            PersonID: [],
                            PersonCustomFiledID: [],
                            RecordType: 1
                        }
                    }
                })
            });
            return await resp.json();
        }
    """)

    records = res.get("RecordResponse", {}).get("RecordList", {}).get("Record", [])
    print(f"🎉 ¡ÉXITO TOTAL! SE OBTUVIERON {len(records)} MARCACIONES REALES DE HIKCENTRAL!")

    if records:
        print("\nPrimera marcación:")
        print(json.dumps(records[0], indent=2, ensure_ascii=False))

    browser.close()
