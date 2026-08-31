import os

print("Buscando carpeta AGOSTO...")
search_roots = [r"G:\Mi unidad", r"G:\Compartidos conmigo", r"G:\\"]
for root in search_roots:
    if os.path.exists(root):
        print(f"Buscando en {root}:")
        for item in os.listdir(root):
            print(f"  - {item}")
