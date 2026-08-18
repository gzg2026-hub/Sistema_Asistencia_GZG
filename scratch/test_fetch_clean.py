import os
import json
import time
from playwright.sync_api import sync_playwright

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

    record_data = res.get("RecordResponse", {}).get("RecordList", {}).get("Record", [])
    print(f"EXITO TOTAL: Se obtuvieron {len(record_data)} marcaciones reales desde HikCentral Access Control.")

    if record_data:
        print("\nEjemplo de las primeras 3 marcaciones:")
        for r in record_data[:3]:
            print("----------------------------------------")
            print("ID Persona:", r.get("PersonID"))
            print("Nombre Completo:", r.get("PersonName"))
            print("ID Trabajador (DNI):", r.get("PersonCode"))
            print("Departamento:", r.get("OrgName"))
            print("Fecha/Hora Marcación:", r.get("RecordTime"))
            print("Punto de Control (Biométrico):", r.get("PointName"))

    browser.close()
