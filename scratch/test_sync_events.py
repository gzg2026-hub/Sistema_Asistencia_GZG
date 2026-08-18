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

# 2. Test SyncEventRecords
sync_url = f"{base_url}/ISAPI/Bumblebee/Integration/V2/SyncEventRecords"

sync_payload = {
    "SyncEventRecordsRequest": {
        "pageIndex": 1,
        "pageSize": 100,
        "startTime": "2026-08-17T00:00:00-05:00",
        "endTime": "2026-08-17T23:59:59-05:00"
    }
}

r = session.post(sync_url, json=sync_payload, timeout=5)
print("SyncEventRecords status:", r.status_code)
print("SyncEventRecords response:", r.text[:800])
