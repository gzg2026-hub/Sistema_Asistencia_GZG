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
    time.sleep(5)

    # Find inputs now after Vue JS loaded
    inputs = page.locator("input").all()
    print(f"Found {len(inputs)} inputs:")
    for idx, inp in enumerate(inputs):
        try:
            ph = inp.get_attribute("placeholder")
            tp = inp.get_attribute("type")
            cls = inp.get_attribute("class")
            print(f"Input {idx}: placeholder='{ph}' type='{tp}' class='{cls}'")
        except Exception:
            pass

    # Find buttons
    btns = page.locator("button, div.el-button, span.el-button").all()
    print(f"\nFound {len(btns)} buttons:")
    for idx, btn in enumerate(btns):
        try:
            txt = btn.inner_text()
            print(f"Button {idx}: text='{txt}'")
        except Exception:
            pass

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "step3_vue_loaded.png"))
    browser.close()
