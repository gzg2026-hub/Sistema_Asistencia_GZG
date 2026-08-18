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

# 2. Record API with form-urlencoded header
record_url = f"{base_url}/ISAPI/Bumblebee/AttendancePlugin/V1/Record?MT=GET"
record_payload_json = json.dumps({
    "RecordRequest": {
        "PageIndex": 1,
        "PageSize": 1000,
        "QueryInfo": {
            "SortInfo": {
                "SortField": 1,
                "SortType": 1
            },
            "BeginTime": "2026-08-01T00:00:00-05:00",
            "EndTime": "2026-08-31T23:59:59-05:00",
            "PersonID": [],
            "PersonCustomFiledID": [],
            "RecordType": 1
        }
    }
})

headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": "https://127.0.0.1/"
}

r = session.post(record_url, data=record_payload_json, headers=headers, timeout=5)
print("Record status:", r.status_code)
print("Record response preview:", r.text[:1200])
