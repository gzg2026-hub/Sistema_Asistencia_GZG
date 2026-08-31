import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file
from core.attendance_engine import procesar_asistencia_df
from data.database import obtener_trabajadores_master

ruta_acum = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
df_marc = parse_hikvision_transaction_file(ruta_acum)

agreda_marc = df_marc[(df_marc['ID'].astype(str).str.contains('47783594')) & (df_marc['Fecha'].astype(str) == '2026-08-20')]

print("=== MARCACIONES RAW DE JHON AGREDA EL 2026-08-20 ===")
for idx, r in agreda_marc.iterrows():
    print(f"ID: {r['ID']} | Fecha: {r['Fecha']} | Tiempo: {r['Tiempo']} | Tipo: {r['Tipo de pase de tarjeta']}")

df_trab = obtener_trabajadores_master()
df_asis, df_he, df_inc, _ = procesar_asistencia_df(df_trab, df_marc)

print("\nColumnas de df_asis:", df_asis.columns.tolist())

agreda_asis = df_asis[(df_asis['DNI'].astype(str).str.contains('47783594')) & (df_asis['FECHA'].astype(str) == '2026-08-20')]
print("\n=== RESULTADO PROCESADO ACTUAL DE JHON AGREDA EL 2026-08-20 ===")
print(agreda_asis.to_string())
