import os
import sys
import openpyxl
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from scripts.download_personal_info import procesar_y_exportar_padron, buscar_ultimo_excel_personal
from data.database import obtener_trabajadores_master

# 1. Buscar el último archivo descargado de personal raw
raw_excel = buscar_ultimo_excel_personal()
print(f"Archivo raw personal encontrado: {raw_excel}")

if raw_excel and os.path.exists(raw_excel):
    res_path = procesar_y_exportar_padron(raw_excel)
    print(f"Padrón procesado en: {res_path}")

# 2. Inspeccionar el contenido de Padron_Trabajadores_GZG.xlsx
padron_path = os.path.join(PROJECT_ROOT, "Padron_Trabajadores_GZG.xlsx")
if os.path.exists(padron_path):
    wb = openpyxl.load_workbook(padron_path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    print(f"Filas totales en Padron_Trabajadores_GZG.xlsx: {len(rows)}")
    for r in rows[:5]:
        print("  Row:", r)
