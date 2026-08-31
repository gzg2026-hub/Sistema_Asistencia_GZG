import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

ruta_live = os.path.join(ROOT_DIR, "downloads", "hikvision", "Transacciones_2026-08-17_2026-08-22.xlsx")
if os.path.exists(ruta_live):
    df_raw = pd.read_excel(ruta_live, sheet_name=0)
    print("--- COLUMNAS Y DATOS REALES DE HIKCENTRAL (WEB CLIENT / PLAYWRIGHT) ---")
    print(f"Total filas: {len(df_raw)}")
    print(f"Columnas ({len(df_raw.columns)}):", df_raw.columns.tolist())
    print("\nPrimeras 5 filas:")
    print(df_raw.head(5))
