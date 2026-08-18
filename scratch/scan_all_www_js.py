import os
import re

www_dir = r"C:\Program Files (x86)\HikCentral Access Control\VSM Servers\Web Service\www"

found = set()

for root, dirs, files in os.walk(www_dir):
    for fname in files:
        if fname.endswith(".js"):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                    matches = set(re.findall(r'ISAPI/Bumblebee/[A-Za-z0-9_/]+', text))
                    for m in matches:
                        if any(k in m.lower() for k in ['acs', 'event', 'trans', 'door', 'card', 'person', 'attend', 'search']):
                            found.add(m)
            except Exception:
                pass

print(f"Found {len(found)} relevant Bumblebee ISAPI endpoints:")
for ep in sorted(found):
    print("  ", ep)
