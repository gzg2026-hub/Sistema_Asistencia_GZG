import os

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
agosto_gdrive = r"G:\.shortcut-targets-by-id\1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU\AGOSTO"

print("=== VERIFICACIÓN FINAL COMPLETA ===")

print("\n1. Archivo local Padron_Trabajadores_GZG.xlsx:")
p_path = os.path.join(PROJECT_ROOT, "Padron_Trabajadores_GZG.xlsx")
if os.path.exists(p_path):
    print(f"   - Existe en PC: {p_path}")
    print(f"   - Tamaño: {os.path.getsize(p_path)} bytes")

print("\n2. Archivos en Google Drive (Carpeta AGOSTO):")
if os.path.exists(agosto_gdrive):
    for f in sorted(os.listdir(agosto_gdrive)):
        print(f"   - {f}")

print("\n3. Verificación de archivos eliminados de Drive:")
print(f"   - Sistema_Asistencia_GZG_v1.0.xlsx en AGOSTO: {os.path.exists(os.path.join(agosto_gdrive, 'Sistema_Asistencia_GZG_v1.0.xlsx'))}")
print(f"   - Padron_Trabajadores_GZG.xlsx en AGOSTO: {os.path.exists(os.path.join(agosto_gdrive, 'Padron_Trabajadores_GZG.xlsx'))}")
