import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

base_url = "https://127.0.0.1"

# 1. Login
login_url = f"{base_url}/ISAPI/Bumblebee/Platform/V0/CheckPassword"
login_payload = {
    "CheckPasswordRequest": {
        "UserName": "admin",
        "Password": "GzG@ACCESO2026"
    }
}

r = session.post(login_url, json=login_payload, timeout=5)
print("Login status:", r.status_code)
print("Login headers:", dict(r.headers))
print("Login cookies:", dict(session.cookies))
print("Login response text:", r.text)

# Also check SlaveSession or KeepLive
kl_url = f"{base_url}/ISAPI/Bumblebee/Platform/V0/KeepLive"
r_kl = session.get(kl_url, timeout=5)
print("\nKeepLive status:", r_kl.status_code, r_kl.text)
