import sys
import os
import json
import time
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from core.hikvision_downloader import cargar_config_hikvision, SWIPE_TYPE_MAP, VERIFY_TYPE_MAP, DIAS_SEMANA
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from playwright.sync_api import sync_playwright

print("Iniciando prueba robusta de descarga...", flush=True)
cfg = cargar_config_hikvision()
base_url = f"{cfg.get('scheme', 'https')}://{cfg.get('host', '127.0.0.1')}"

fecha_inicio = "2026-08-18"
fecha_fin = "2026-08-18"

records = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--no-sandbox"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.goto(f"{base_url}/#/", wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)

    # Remover readonly y forzar llenado vía evaluate
    page.evaluate(f"""
        () => {{
            const inputs = document.querySelectorAll('input');
            inputs.forEach(i => i.removeAttribute('readonly'));
            const u = document.querySelector('#username') || inputs[0];
            const p = document.querySelector('input[type=password]') || inputs[1];
            if (u) {{
                u.value = '{cfg.get("username", "admin")}';
                u.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            if (p) {{
                p.value = '{cfg.get("password", "GzG@ACCESO2026")}';
                p.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }}
    """)

    login_btn = page.locator("button:has-text('Iniciar'), button:has-text('Log In'), button[type='button']").first
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
    print("RES COMPLETO:", json.dumps(res, indent=2), flush=True)
    records = res.get("ResponseStatus", {}).get("Data", {}).get("OriginalRecord", [])
    print(f"REGISTROS EXTRAIDOS: {len(records)} marcaciones.", flush=True)
