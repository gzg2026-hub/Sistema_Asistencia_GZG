import os
import time
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--ignore-certificate-errors", "--no-sandbox"]
    )
    context = browser.new_context(ignore_https_errors=True, accept_downloads=True)
    page = context.new_page()

    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded")
    time.sleep(6)

    print("Page URL after 6s:", page.url)

    # Dump all visible text on the page
    text = page.locator("body").inner_text()
    print("Page body text preview:", text[:600])

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "step2_dashboard.png"))
    browser.close()
