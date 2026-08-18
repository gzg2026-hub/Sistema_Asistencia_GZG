import os
import re

report_dir = r"C:\Program Files (x86)\HikCentral Access Control\VSM Servers\Web Service\www\Report"

for root, dirs, files in os.walk(report_dir):
    for fname in files:
        if fname.endswith(".js"):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                    matches = set(re.findall(r'["\'](/ISAPI/[^"\']+|ISAPI/[^"\']+|/artemis/[^"\']+)["\']', text))
                    if matches:
                        print(f"\n--- {fname} ({len(matches)} matches) ---")
                        for m in sorted(matches):
                            print(f"  {m}")
            except Exception as e:
                pass
