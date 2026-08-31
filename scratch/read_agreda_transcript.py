import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

log_file = r"C:\Users\GZG Minerales 2026\.gemini\antigravity-ide\brain\dae2bec7-1220-47ba-80aa-e9ba376d6d00\.system_generated\logs\transcript.jsonl"

with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        if "agreda" in line.lower():
            data = json.loads(line)
            content = data.get("content", "")
            if "USER" in str(data.get("type", "")):
                print("--- MENSAJE DEL USUARIO ---")
                print(content)
                print("-" * 50)
