import os
import re
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

for js_name in ["main.js", "common.js", "components.js"]:
    url = f"https://127.0.0.1/Common/{js_name}"
    try:
        r = session.get(url, timeout=10)
        bumblebee_endpoints = set(re.findall(r'ISAPI/Bumblebee/[a-zA-Z0-9_/]+', r.text))
        print(f"\n--- {js_name}: Found {len(bumblebee_endpoints)} Bumblebee ISAPI endpoints ---")
        for ep in sorted(bumblebee_endpoints):
            if any(k in ep.lower() for k in ['event', 'acs', 'report', 'card', 'person', 'trans', 'login', 'pass', 'auth', 'record', 'search', 'query']):
                print(f"  {ep}")
    except Exception as e:
        print(f"Error {js_name}: {e}")
