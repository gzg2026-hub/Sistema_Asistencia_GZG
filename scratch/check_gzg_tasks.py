import subprocess

res = subprocess.run(["schtasks", "/Query", "/FO", "LIST"], capture_output=True, text=True)
tasks = []
curr = {}
for line in res.stdout.splitlines():
    if line.startswith("Nombre de tarea:"):
        if curr:
            tasks.append(curr)
        curr = {"name": line.split(":", 1)[1].strip()}
    elif line.startswith("Hora pr") and curr:
        curr["next"] = line.split(":", 1)[1].strip()
    elif line.startswith("Estado:") and curr:
        curr["state"] = line.split(":", 1)[1].strip()

if curr:
    tasks.append(curr)

print("TAREAS GZG REGISTRADAS:")
for t in tasks:
    if "GZG" in t.get("name", ""):
        print(" ", t)
