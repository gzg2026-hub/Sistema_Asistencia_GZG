import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

base_url = "https://127.0.0.1"

# 1. Get Crypto
crypto_url = f"{base_url}/ISAPI/Bumblebee/Platform/V0/Security/Crypto"
r = session.get(crypto_url, timeout=5)
print("Crypto status:", r.status_code)
print("Crypto response:", r.text)

# 2. Test preLogin or login endpoints
endpoints = [
    "/ISAPI/Bumblebee/Platform/V0/Security/PreLogin",
    "/ISAPI/Bumblebee/Platform/V0/Security/Login",
    "/ISAPI/Bumblebee/Platform/V0/SecuritySetting"
]

for ep in endpoints:
    url = f"{base_url}{ep}"
    try:
        r = session.get(url, timeout=5)
        print(f"\nGET {ep} -> Status {r.status_code}")
        print("Response:", r.text[:300])
    except Exception as e:
        print(f"GET {ep} Error:", e)
