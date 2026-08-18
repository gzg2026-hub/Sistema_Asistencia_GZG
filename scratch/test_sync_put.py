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

# 2. Put SyncEventRecords
sync_url = f"{base_url}/ISAPI/Bumblebee/Integration/V2/SyncEventRecords"

sync_payload = {
    "SyncEventRecordsRequest": {
        "BeginTime": "2026/08/17 00:00:00",
        "EndTime": "2026/08/17 23:59:59"
    }
}

r = session.put(sync_url, json=sync_payload, timeout=5)
print("SyncEventRecords PUT status:", r.status_code)
print("SyncEventRecords PUT response:", r.text)

# 3. Check SyncStatus
status_url = f"{base_url}/ISAPI/Bumblebee/Integration/V2/SyncEventRecordsStatus"
r = session.get(status_url, timeout=5)
print("\nSyncStatus GET status:", r.status_code)
print("SyncStatus GET response:", r.text)
