import re

with open("scratch/login_page.html", "r", encoding="utf-8") as f:
    html = f.read()

inputs = re.findall(r'<input[^>]*>', html)
print("--- INPUTS ---")
for i in inputs:
    print(i)

buttons = re.findall(r'<button[^>]*>.*?</button>', html, re.DOTALL)
print("\n--- BUTTONS ---")
for b in buttons:
    print(b)
