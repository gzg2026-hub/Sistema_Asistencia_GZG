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

# 2. Test endpoints
urls = [
    f"{base_url}/ISAPI/Bumblebee/AttendancePlugin/V1/AttendanceReport/ReportTypes",
    f"{base_url}/ISAPI/Bumblebee/AttendancePlugin/V1/AttendanceGroup",
    f"{base_url}/ISAPI/Bumblebee/DeviceResource/V1/LogicalResource/Elements?pageIndex=1&pageSize=10",
    f"{base_url}/ISAPI/Bumblebee/DeviceResource/V1/PhysicalResource/Devices?pageIndex=1&pageSize=10"
]

for url in urls:
    r = session.get(url, timeout=5)
    print(f"\nGET {url} -> Status {r.status_code}")
    print("Response:", r.text[:400])
