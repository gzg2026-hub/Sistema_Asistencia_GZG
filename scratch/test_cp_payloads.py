import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

base_url = "https://127.0.0.1"
user = "admin"
pwd = "GzG@ACCESO2026"

url = f"{base_url}/ISAPI/Bumblebee/Platform/V0/CheckPassword"

payloads = [
    {"CheckPasswordRequest": {"UserName": user, "Password": pwd}},
    {"CheckPasswordRequest": {"userName": user, "password": pwd}},
    {"CheckPasswordRequest": {"username": user, "password": pwd}},
    {"CheckPasswordRequest": {"UserName": user, "Password": pwd, "AccountType": 0}}
]

for p in payloads:
    r = session.post(url, json=p, timeout=5)
    print(f"POST {p} -> Status {r.status_code}")
    print(f"  Response: {r.text}\n")
