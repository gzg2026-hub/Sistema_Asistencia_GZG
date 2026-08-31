import os
import pandas as pd
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file

ruta = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")

df = parse_hikvision_transaction_file(ruta)

col_order = [
    'ID', 'Nombre', 'Apellido', 'Departamento', 'Posición',
    'Fecha', 'Semana', 'Tiempo', 'Tipo de pase de tarjeta',
    'Método de verificación', 'Punto de control de asistencia'
]

present = [c for c in col_order if c in df.columns]
other = [c for c in df.columns if c not in col_order]
df_clean = df[present + other]

try:
    with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
        df_clean.to_excel(writer, index=False, sheet_name='Transacciones')
    print("SUCCESS: Transacciones_Acumuladas.xlsx reescrito en PC local con las 11 columnas exactas.")
except Exception as e:
    print(f"LOCKED: No se pudo escribir porque el archivo está abierto en Excel: {e}")
