import os
import sys
import shutil

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

local_padron = os.path.join(PROJECT_ROOT, "Padron_Trabajadores_GZG.xlsx")

# Rutas de Google Drive
agosto_dir = r"G:\.shortcut-targets-by-id\1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU\AGOSTO"
asistencia_parent_dir = r"G:\.shortcut-targets-by-id\1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"

print("=== APLICANDO REGLAS DE ESTRUCTURA Y ARCHIVOS DE GOOGLE DRIVE ===")

# 1. Eliminar Sistema_Asistencia_GZG_v1.0.xlsx de Google Drive (solo queda local)
files_to_delete_from_drive = [
    os.path.join(agosto_dir, "Sistema_Asistencia_GZG_v1.0.xlsx"),
    os.path.join(asistencia_parent_dir, "Sistema_Asistencia_GZG_v1.0.xlsx"),
    os.path.join(r"G:\Mi unidad", "Sistema_Asistencia_GZG_v1.0.xlsx"),
    os.path.join(agosto_dir, "Padron_Trabajadores_GZG.xlsx"), # Quitar de agosto
]

for p in files_to_delete_from_drive:
    if os.path.exists(p):
        try:
            os.remove(p)
            print(f"[OK] Eliminado de Google Drive: {p}")
        except Exception as e:
            print(f"[Aviso] No se pudo borrar {p}: {e}")

# 2. Copiar Padron_Trabajadores_GZG.xlsx al nivel superior ASISTENCIA
if os.path.exists(asistencia_parent_dir):
    dest_padron = os.path.join(asistencia_parent_dir, "Padron_Trabajadores_GZG.xlsx")
    with open(local_padron, "rb") as src_f:
        data = src_f.read()
    with open(dest_padron, "wb") as dst_f:
        dst_f.write(data)
    print(f"[OK] Padrón de Trabajadores copiado al nivel superior ASISTENCIA -> {dest_padron}")

print("\n--- Estado de archivos en Google Drive carpeta AGOSTO ---")
if os.path.exists(agosto_dir):
    for f in sorted(os.listdir(agosto_dir)):
        print(f"  - {f}")

print("\n--- Estado de archivos en Google Drive carpeta ASISTENCIA (Nivel Superior) ---")
if os.path.exists(asistencia_parent_dir):
    for f in sorted(os.listdir(asistencia_parent_dir)):
        if os.path.isfile(os.path.join(asistencia_parent_dir, f)):
            print(f"  - [Archivo] {f}")
        else:
            print(f"  - [Carpeta] {f}")
