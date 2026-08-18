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

# 2. Get Elements
elem_url = f"{base_url}/ISAPI/Bumblebee/DeviceResource/V1/LogicalResource/Elements"
elem_payload = {
    "ElementsRequest": {
        "SiteID": 0,
        "AreaID": -1,
        "PageIndex": 1,
        "PageSize": 50
    }
}

r = session.post(elem_url, json=elem_payload, timeout=5)
print("\nElements status:", r.status_code)
print("Elements response:", r.text[:800])
