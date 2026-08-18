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

matches = set(re.findall(r'url\s*:\s*["\']([^"\']*Event[^"\']*)["\']', text, re.IGNORECASE))
matches.update(re.findall(r'url\s*:\s*["\']([^"\']*Acs[^"\']*)["\']', text, re.IGNORECASE))
matches.update(re.findall(r'url\s*:\s*["\']([^"\']*Report[^"\']*)["\']', text, re.IGNORECASE))
matches.update(re.findall(r'url\s*:\s*["\']([^"\']*Trans[^"\']*)["\']', text, re.IGNORECASE))
matches.update(re.findall(r'url\s*:\s*["\']([^"\']*Door[^"\']*)["\']', text, re.IGNORECASE))

print(f"Found {len(matches)} event/report related URLs in common.js:")
for m in sorted(matches):
    print("  ", m)
