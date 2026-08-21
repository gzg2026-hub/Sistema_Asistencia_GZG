import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from core.hikvision_downloader import descargar_transacciones_hikvision

path = descargar_transacciones_hikvision(fecha_inicio="2026-08-18", fecha_fin="2026-08-19")
print("Downloaded file path:", path)
