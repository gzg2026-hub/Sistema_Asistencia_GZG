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

print("Searching for URL patterns in common.js...")
matches = set(re.findall(r'/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+', text))
interesting = [m for m in matches if any(k in m.lower() for k in ['login', 'acs', 'event', 'auth', 'user', 'report', 'card', 'person', 'trans', 'search', 'query', 'token'])]
print(f"Found {len(interesting)} interesting endpoint patterns:")
for m in sorted(interesting)[:40]:
    print(f"  {m}")
