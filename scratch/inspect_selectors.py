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

    page.goto("https://127.0.0.1/#/", wait_until="networkidle")
    time.sleep(3)

    # Fill login if present
    print("Page title:", page.title())
    print("Page URL:", page.url)

    # Check inputs
    inputs = page.locator("input").all()
    print(f"Found {len(inputs)} inputs:")
    for idx, inp in enumerate(inputs):
        try:
            print(f"Input {idx}: placeholder={inp.get_attribute('placeholder')} type={inp.get_attribute('type')} class={inp.get_attribute('class')}")
        except Exception:
            pass

    page.screenshot(path=os.path.join(PROJECT_ROOT, "scratch", "step1_login.png"))
    browser.close()
