import os
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--ignore-certificate-errors", "--no-sandbox"]
    )
    context = browser.new_context(ignore_https_errors=True, accept_downloads=True)
    page = context.new_page()

    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded")
    time.sleep(4)

    page.evaluate("document.querySelectorAll('input').forEach(i => i.removeAttribute('readonly'))")
    page.locator("#username, input[placeholder='Nombre de usuario']").first.fill("admin")
    page.locator("input[type='password']").first.fill("GzG@ACCESO2026")
    page.locator("button:has-text('Iniciar')").first.click()
    time.sleep(5)

    elements = page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('*'))
                .filter(e => e.children.length === 0 && e.textContent.trim() === 'Asistencia')
                .map(e => ({
                    tag: e.tagName,
                    className: e.className,
                    id: e.id,
                    outerHTML: e.outerHTML
                }));
        }
    """)

    print(f"Found {len(elements)} leaf elements with text 'Asistencia':")
    for el in elements:
        print(el)

    browser.close()
