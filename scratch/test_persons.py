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

# 2. Get Persons list
url = f"{base_url}/ISAPI/Bumblebee/Platform/V1/PersonCredential/Persons?pageIndex=1&pageSize=10"
r = session.get(url, timeout=5)
print("\nGET Persons status:", r.status_code)
print("Persons response:", r.text[:500])
