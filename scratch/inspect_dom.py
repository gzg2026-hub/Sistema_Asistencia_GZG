import sys
import os
import json
import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--no-sandbox"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://127.0.0.1/#/", wait_until="domcontentloaded", timeout=15000)
    time.sleep(4)

    page.screenshot(path="scratch/login_page.png")
    html = page.content()
    with open("scratch/login_page.html", "w", encoding="utf-8") as f:
        f.write(html)

    browser.close()

print("Screenshot guardado en scratch/login_page.png", flush=True)
