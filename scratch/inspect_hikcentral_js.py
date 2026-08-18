import os
import re
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

js_urls = [
    "https://127.0.0.1/Common/app.js",
    "https://127.0.0.1/Common/main.js",
    "https://127.0.0.1/Common/common.js"
]

for js_url in js_urls:
    print(f"Downloading {js_url}...")
    try:
        r = session.get(js_url, timeout=10)
        print(f"  Downloaded {len(r.text)} bytes")
        # Search for API endpoints in JS code
        api_matches = set(re.findall(r'["\'](/artemis/[^"\']+|/api/[^"\']+|/bms/[^"\']+|/cas/[^"\']+|/portal/[^"\']+)["\']', r.text))
        login_matches = [m for m in api_matches if 'login' in m.lower() or 'event' in m.lower() or 'acs' in m.lower() or 'auth' in m.lower()]
        print(f"  API matches related to login/events ({len(login_matches)}):")
        for m in sorted(login_matches)[:30]:
            print(f"    {m}")
    except Exception as e:
        print(f"  Error: {e}")
