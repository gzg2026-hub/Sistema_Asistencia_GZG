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

# 2. Get Devices
dev_url = f"{base_url}/ISAPI/Bumblebee/DeviceResource/V1/PhysicalResource/Devices"
r = session.post(dev_url, json={"DeviceSearchRequest": {"PageIndex": 1, "PageSize": 100}}, timeout=5)
print("Get Devices status:", r.status_code)
print("Get Devices response:", r.text[:600])

# 3. Test HTTPPassThrough
pt_url = f"{base_url}/ISAPI/Bumblebee/Platform/V1/DAM/HTTPPassThrough"
pt_payload = {
    "HTTPPassThroughRequest": {
        "url": "/ISAPI/AccessControl/AcsEvent?format=json",
        "method": "POST",
        "content": json.dumps({
            "AcsEventCond": {
                "searchID": "1",
                "searchResultPosition": 0,
                "maxResults": 100
            }
        })
    }
}
r = session.post(pt_url, json=pt_payload, timeout=5)
print("\nHTTPPassThrough status:", r.status_code)
print("HTTPPassThrough response:", r.text[:600])
