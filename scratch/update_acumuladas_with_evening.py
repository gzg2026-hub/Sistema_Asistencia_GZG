import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import cargar_datos_excel, fusionar_y_deduplicar_data_cruda
from data.exporter import guardar_transacciones_acumuladas_excel

ruta_live = os.path.join(ROOT_DIR, "downloads", "hikvision", "Transacciones_2026-08-17_2026-08-22.xlsx")
_, df_marc_nuevo, _ = cargar_datos_excel(ruta_live)

ruta_maestro_raw = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")

df_master = fusionar_y_deduplicar_data_cruda(df_marc_nuevo, ruta_maestro_raw)
guardar_transacciones_acumuladas_excel(df_master, ruta_maestro_raw)

print(f"Transacciones_Acumuladas.xlsx actualizado con exito!")
print(f"Total de marcaciones guardadas (manana + tarde/noche): {len(df_master)}")
