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

matches = re.findall(r'data\s*:\s*\{([A-Za-z0-9_]+Request:[^\}]+)\}', text)
print(f"Found {len(matches)} Request payloads in common.js:")
for m in sorted(set(matches))[:40]:
    print(f"  {m}")
