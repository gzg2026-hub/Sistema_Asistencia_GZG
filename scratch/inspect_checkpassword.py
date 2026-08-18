import os
import re
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

r = session.get("https://127.0.0.1/Common/common.js", timeout=10)
text = r.text

idx = text.find("CheckPassword")
if idx != -1:
    print("Found CheckPassword at index", idx)
    print(text[max(0, idx-300):min(len(text), idx+500)])
else:
    print("CheckPassword not found")
