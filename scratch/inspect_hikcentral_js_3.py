import os
import re
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

r = session.get("https://127.0.0.1/Common/common.js", timeout=10)
text = r.text

print("Searching for login API calls...")
matches = re.findall(r'url\s*:\s*["\']([^"\']+)["\']', text)
print(f"Found {len(matches)} url properties in JS:")
urls = set(matches)
login_urls = [u for u in urls if any(k in u.lower() for k in ['login', 'auth', 'token', 'event', 'acs', 'api', 'user', 'hcp', 'artemis'])]
for u in sorted(login_urls)[:40]:
    print(f"  {u}")
