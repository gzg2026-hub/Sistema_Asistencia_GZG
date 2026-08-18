import os
import re

www_dir = r"C:\Program Files (x86)\HikCentral Access Control\VSM Servers\Web Service\www"

for root, dirs, files in os.walk(www_dir):
    for fname in files:
        if fname.endswith(".js"):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                    if "Huella" in text or "VerifyType" in text or "verifyType" in text:
                        idx = text.find("VerifyType")
                        if idx == -1:
                            idx = text.find("verifyType")
                        if idx != -1:
                            print(f"\n--- Found VerifyType in {fname} at {idx} ---")
                            print(text[max(0, idx-100):min(len(text), idx+500)])
            except Exception:
                pass
