import os

fpath = r"C:\Program Files (x86)\HikCentral Access Control\VSM Servers\Web Service\www\319_chunk.600339b2f233c9eb7653.js"

with open(fpath, "r", encoding="utf-8") as f:
    text = f.read()
    idx = text.find("login:function")
    if idx != -1:
        print("Found login:function at", idx)
        print(text[max(0, idx-100):min(len(text), idx+400)])
