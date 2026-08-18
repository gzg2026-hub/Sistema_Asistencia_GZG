import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

base_url = "https://127.0.0.1"

login_url = f"{base_url}/ISAPI/Bumblebee/Platform/V0/CheckPassword"
login_payload = {
    "CheckPasswordRequest": {
        "UserName": "admin",
        "Password": "GzG@ACCESO2026"
    }
}
r = session.post(login_url, json=login_payload, timeout=5)

record_url = f"{base_url}/ISAPI/Bumblebee/AttendancePlugin/V1/Record?MT=GET"
record_payload = {
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
}

r = session.post(record_url, json=record_payload, timeout=5)
print("Status:", r.status_code)
print("Text:", r.text)
