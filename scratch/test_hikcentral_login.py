import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

base_url = "https://127.0.0.1"
user = "admin"
pwd = "GzG@ACCESO2026"

print(f"Probando login en HikCentral Web Client ({base_url})...")

# 1. Check Version / Session Login capabilities
res = session.get(f"{base_url}/ISAPI/Bumblebee/Platform/V0/Version")
print(f"Version status: {res.status_code} | {res.text[:200]}")

# 2. Check password / auth
login_payloads = [
    {"username": user, "password": pwd},
    {"userName": user, "password": pwd},
    {"user": user, "password": pwd},
    {"CheckPassword": {"username": user, "password": pwd}}
]

for p in login_payloads:
    try:
        r = session.post(f"{base_url}/ISAPI/Bumblebee/Platform/V0/CheckPassword", json=p, timeout=5)
        print(f"CheckPassword {p} -> {r.status_code} | {r.text[:200]}")
    except Exception as e:
        print(f"Error CheckPassword: {e}")
