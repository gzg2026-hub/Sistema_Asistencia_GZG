import sqlite3
import pandas as pd
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file, cargar_datos_excel
from core.attendance_engine import time_to_seconds

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
df_acum = parse_hikvision_transaction_file(ruta_acumuladas)

df_jf17 = df_acum[(df_acum['ID'].astype(str).str.contains('70782038')) & (df_acum['Fecha'] == '2026-08-17')]
print("\n=== MARCACIONES JUAN FERNANDO 2026-08-17 ===")
for idx, r in df_jf17.iterrows():
    print(dict(r))
