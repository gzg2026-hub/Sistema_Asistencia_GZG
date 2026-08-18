import os
import sys
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg_path = os.path.join(ROOT, "config_hikvision.json")

with open(cfg_path, "r", encoding="utf-8") as f:
    cfg = json.load(f)

host = cfg.get("host", "127.0.0.1")
scheme = cfg.get("scheme", "https")
port = cfg.get("port", 443)
user = cfg.get("username", "admin")
pwd = cfg.get("password", "GzG@ACCESO2026")

base_url = f"{scheme}://{host}:{port}" if port != 443 else f"{scheme}://{host}"
print(f"Probando conexion a {base_url} como usuario '{user}'...")

# 1. Probar ISAPI en https://127.0.0.1
endpoints = [
    f"{base_url}/ISAPI/AccessControl/AcsEvent?format=json",
    f"{base_url}/ISAPI/System/deviceInfo?format=json",
    f"{base_url}/ISAPI/Security/sessionLogin/capabilities?format=json"
]

auth_digest = requests.auth.HTTPDigestAuth(user, pwd)
auth_basic = requests.auth.HTTPBasicAuth(user, pwd)

for ep in endpoints:
    print(f"\n--- Probando: {ep} ---")
    for name, auth in [("Digest", auth_digest), ("Basic", auth_basic), ("None", None)]:
        try:
            res = requests.get(ep, auth=auth, verify=False, timeout=5)
            print(f"[{name}] GET -> Status: {res.status_code}")
            if res.status_code == 200:
                print(f"  Respuesta: {res.text[:300]}")
        except Exception as e:
            print(f"  [{name}] GET Error: {e}")

        try:
            payload = {
                "AcsEventCond": {
                    "searchID": "1",
                    "searchResultPosition": 0,
                    "maxResults": 10
                }
            }
            res = requests.post(ep, json=payload, auth=auth, verify=False, timeout=5)
            print(f"[{name}] POST -> Status: {res.status_code}")
            if res.status_code == 200:
                print(f"  Respuesta: {res.text[:300]}")
        except Exception as e:
            print(f"  [{name}] POST Error: {e}")
