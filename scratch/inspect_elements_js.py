import os
import re

resource_dir = r"C:\Program Files (x86)\HikCentral Access Control\VSM Servers\Web Service\www\Resource"

for root, dirs, files in os.walk(resource_dir):
    for fname in files:
        if fname.endswith(".js"):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                    idx = text.find("LogicalResource/Elements")
                    if idx != -1:
                        print(f"\n--- {fname} at {idx} ---")
                        print(text[max(0, idx-100):min(len(text), idx+400)])
            except Exception:
                pass
