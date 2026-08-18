import os
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

for js_name in ["common.js", "components.js", "delegate.js", "addon.js"]:
    url = f"https://127.0.0.1/Common/{js_name}"
    try:
        r = session.get(url, timeout=10)
        endpoints = set(re.findall(r'ISAPI/[a-zA-Z0-9_/]+', r.text))
        print(f"\n--- {js_name}: Found {len(endpoints)} ISAPI endpoints ---")
        for ep in sorted(endpoints):
            print(f"  {ep}")
    except Exception as e:
        print(f"Error {js_name}: {e}")
