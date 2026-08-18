import os
import re

report_dir = r"C:\Program Files (x86)\HikCentral Access Control\VSM Servers\Web Service\www"

found = set()
for root, dirs, files in os.walk(report_dir):
    for fname in files:
        if fname.endswith(".js"):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                    matches = set(re.findall(r'url\s*:\s*["\']([^"\']+)["\']', text))
                    for m in matches:
                        if any(k in m.lower() for k in ['event', 'record', 'search', 'query', 'acs', 'report', 'card', 'swipe', 'pass', 'log']):
                            found.add(m)
            except Exception:
                pass

print(f"Found {len(found)} URL matches in all JS files:")
for u in sorted(found)[:60]:
    print("  ", u)
