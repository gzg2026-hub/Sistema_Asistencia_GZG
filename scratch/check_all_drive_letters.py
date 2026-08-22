import os
import string

print("=== BUSCANDO RUTA LOCAL DE GOOGLE DRIVE EN WINDOWS ===")

# Buscar letras de unidades activas
for letter in string.ascii_uppercase:
    drive = f"{letter}:\\"
    if os.path.exists(drive):
        print(f"Unidad detectada: {drive}")
        try:
            items = os.listdir(drive)
            for it in items:
                print(f"   [{letter}:] -> {it}")
        except Exception as e:
            print(f"   [{letter}:] Error: {e}")

# Buscar en AppData o Local profiles
user_home = os.path.expanduser("~")
print(f"\nUser home: {user_home}")
try:
    for root, dirs, files in os.walk(user_home):
        if "ASISTENCIA" in root.upper() or "AGOSTO" in root.upper():
            print(f"Carpeta encontrada: {root}")
        if len(root.split(os.sep)) > 6:
            dirs.clear() # Limitar profundidad
except Exception as e:
    pass
