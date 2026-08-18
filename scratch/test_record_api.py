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

# 2. Query Record endpoint
record_url = f"{base_url}/ISAPI/Bumblebee/AttendancePlugin/V1/Record?MT=GET"
record_payload = {
    "RecordRequest": {
        "PageIndex": 1,
        "PageSize": 1000
    }
}

r = session.post(record_url, json=record_payload, timeout=5)
print("Record status:", r.status_code)
print("Record response preview:", r.text[:1200])
