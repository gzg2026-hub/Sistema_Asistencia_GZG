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
print("Login status:", r.status_code, r.text)

# 2. Test endpoints after login
endpoints_to_test = [
    ("/ISAPI/Bumblebee/DeviceResource/V1/PhysicalResource/Devices", "GET", None),
    ("/ISAPI/Bumblebee/DeviceResource/V1/LogicalResource/Elements", "GET", None),
    ("/ISAPI/AccessControl/AcsEvent?format=json", "POST", {
        "AcsEventCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 100
        }
    }),
    ("/ISAPI/AccessControl/AcsEventSearch?format=json", "POST", {
        "AcsEventSearchCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 100
        }
    })
]

for path, method, body in endpoints_to_test:
    url = f"{base_url}{path}"
    print(f"\n--- Testing {method} {path} ---")
    try:
        if method == "GET":
            res = session.get(url, timeout=5)
        else:
            res = session.post(url, json=body, timeout=5)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text[:400]}")
    except Exception as e:
        print("Error:", e)
