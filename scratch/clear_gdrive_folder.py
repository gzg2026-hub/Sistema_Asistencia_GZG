import os

gdrive_sync_dirs = [
    r"G:\.shortcut-targets-by-id\1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU\AGOSTO",
    r"G:\.shortcut-targets-by-id\1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU",
]

deleted_count = 0

for sync_dir in gdrive_sync_dirs:
    if os.path.exists(sync_dir):
        print(f"Buscando archivos en: {sync_dir}")
        for item in os.listdir(sync_dir):
            item_path = os.path.join(sync_dir, item)
            if os.path.isfile(item_path) and (item.endswith(".xlsx") or item.endswith(".csv")):
                try:
                    os.remove(item_path)
                    print(f"ELIMINADO DE DRIVE: {item}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Aviso eliminando {item}: {e}")

print(f"\nLIMPIEZA COMPLETADA! Se eliminaron {deleted_count} archivos de la carpeta AGOSTO de Google Drive.")
