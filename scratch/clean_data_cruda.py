import os

data_cruda_dir = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda"

print(f"Limpiando carpeta: {data_cruda_dir}")

deleted_files = []
kept_files = []

for item in os.listdir(data_cruda_dir):
    item_path = os.path.join(data_cruda_dir, item)
    if os.path.isfile(item_path):
        if item.strip().lower() == "transacciones_acumuladas.xlsx":
            kept_files.append(item)
        else:
            try:
                os.remove(item_path)
                deleted_files.append(item)
                print(f"ELIMINADO: {item}")
            except Exception as e:
                print(f"Error al eliminar {item}: {e}")

print("\nLIMPIEZA DE DATA_CRUDA COMPLETADA!")
print(f"Conservado únicamente: {kept_files}")
print(f"Total eliminados: {len(deleted_files)}")
