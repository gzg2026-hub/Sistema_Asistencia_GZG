import os
import sys
from playwright.sync_api import sync_playwright

folder_url = "https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"
test_file = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\archivo_prueba_gzg.txt"

with open(test_file, "w", encoding="utf-8") as f:
    f.write("Archivo de prueba de sincronizacion automatica GZG Minerales 2026\n")

print(f"Archivo de prueba creado: {test_file}")

# Verificar rutas de Google Drive local en Windows
possible_drive_paths = [
    r"G:\Mi unidad",
    r"G:\Shared drives",
    r"G:\Compartidos conmigo",
    r"C:\Users\GZG Minerales 2026\Google Drive",
    r"C:\Users\GZG Minerales 2026\Drive",
    os.path.expanduser(r"~\Google Drive"),
]

found_local = False
for p in possible_drive_paths:
    if os.path.exists(p):
        print(f"Local Google Drive path found: {p}")
        found_local = True

if not found_local:
    print("Buscando carpetas en unidades locales...")
    for drive_letter in ["G", "H", "I", "D", "E"]:
        d_path = f"{drive_letter}:\\"
        if os.path.exists(d_path):
            print(f"Unidad detectada: {d_path}")
            try:
                for item in os.listdir(d_path):
                    print(f"   - {item}")
            except Exception as e:
                pass
