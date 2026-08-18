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

    def handle_request(req):
        if "Record" in req.url:
            print("\n================ RECORD REQUEST ================")
            print("URL:", req.url)
            print("Method:", req.method)
            print("Headers:", req.headers)
            print("Post Data:", req.post_data)

    def handle_response(res):
        if "Record" in res.url:
            print("\n================ RECORD RESPONSE ================")
            print("Status:", res.status)
            try:
                print("Text preview:", res.text()[:800])
            except Exception:
                pass

    page.on("request", handle_request)
    page.on("response", handle_response)

    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded")
    time.sleep(4)

    page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
    page.locator("#username, input[placeholder='Nombre de usuario']").first.fill("admin")
    page.locator("input[type='password']").first.fill("GzG@ACCESO2026")
    page.locator("button:has-text('Iniciar')").first.click()
    time.sleep(5)

    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Asistencia' && e.offsetHeight > 0);
            if (el) el.click();
        }
    """)
    time.sleep(3)

    page.evaluate("""
        () => {
            const el = Array.from(document.querySelectorAll('div, span, li'))
                .find(e => e.textContent.trim() === 'Transacciones');
            if (el) el.click();
        }
    """)
    time.sleep(4)

    browser.close()
