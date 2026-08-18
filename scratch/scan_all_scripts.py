import os
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

r = session.get("https://127.0.0.1/", timeout=5)
# Find all script src tags
scripts = re.findall(r'src=["\']([^"\']+)["\']', r.text)
print("Scripts loaded by index.html:", scripts)

for s in scripts:
    clean_s = s.lstrip('./')
    url = f"https://127.0.0.1/{clean_s}"
    try:
        res = session.get(url, timeout=10)
        print(f"\nScanning {clean_s} ({len(res.text)} bytes)...")
        # Search for Bumblebee URLs
        urls = set(re.findall(r'ISAPI/Bumblebee/[A-Za-z0-9_/]+', res.text))
        if urls:
            print(f"  Found {len(urls)} Bumblebee endpoints:")
            for u in sorted(urls):
                print(f"    {u}")
    except Exception as e:
        print(f"Error {clean_s}: {e}")
