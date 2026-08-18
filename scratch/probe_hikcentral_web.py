import os
import re
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

url = "https://127.0.0.1/"
r = session.get(url)
print(f"GET {url} -> Status {r.status_code}")
print("HTML sample:")
print(r.text[:500])

# Find JS file links in HTML
js_files = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text)
print(f"\nJS bundle files found: {js_files}")

# Probe common API paths for HikCentral Web Client
paths = [
    "/api/login",
    "/api/v1/login",
    "/api/v1/auth/login",
    "/action/login",
    "/cas/login",
    "/artemis/api/v1/oauth/token",
    "/api/common/login",
    "/api/user/login",
    "/api/acs/v1/door/events",
    "/api/event/search",
    "/api/acs/events"
]

for p in paths:
    target = f"https://127.0.0.1{p}"
    try:
        res = session.post(target, json={"username": "admin", "password": "GzG@ACCESO2026"}, timeout=3)
        print(f"POST {p} -> {res.status_code} | {res.text[:150]}")
    except Exception as e:
        print(f"POST {p} -> Error: {e}")
