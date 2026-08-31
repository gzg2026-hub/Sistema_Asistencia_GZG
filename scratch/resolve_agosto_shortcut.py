import os

shortcut_base = r"G:\.shortcut-targets-by-id"
if os.path.exists(shortcut_base):
    print("Contenido de .shortcut-targets-by-id:")
    for root, dirs, files in os.walk(shortcut_base):
        print(f"Directorio: {root}")
        for d in dirs:
            print(f"  [DIR] {d}")
        for f in files:
            print(f"  [FILE] {f}")
else:
    print(".shortcut-targets-by-id no existe")
