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

matches = [m.start() for m in re.finditer(r'CheckPasswordRequest', text)]
print(f"Found {len(matches)} occurrences of CheckPasswordRequest in common.js")

for idx in matches:
    print("\n--- Match snippet ---")
    print(text[max(0, idx-100):min(len(text), idx+400)])
