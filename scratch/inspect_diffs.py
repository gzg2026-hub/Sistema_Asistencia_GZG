import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file

ruta_live = os.path.join(ROOT_DIR, "downloads", "hikvision", "Transacciones_2026-08-17_2026-08-22.xlsx")
df_live_raw = pd.read_excel(ruta_live, sheet_name=0)

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
df_acum = parse_hikvision_transaction_file(ruta_acumuladas)

def clean_dni(val):
    s = str(val).strip()
    # Extraer digitos
    digits = ''.join(c for c in s if c.isdigit())
    if digits:
        return str(int(digits))
    return s

df_live_raw['key'] = df_live_raw['DNI'].apply(clean_dni) + "_" + df_live_raw['FECHA'].astype(str).str.strip() + "_" + df_live_raw['HORA'].astype(str).str.strip()
df_acum['key'] = df_acum['ID'].apply(clean_dni) + "_" + df_acum['Fecha'].astype(str).str.strip() + "_" + df_acum['Tiempo'].astype(str).str.strip()

live_keys = set(df_live_raw['key'])
acum_keys = set(df_acum['key'])

diferencia_live_acum = live_keys - acum_keys
diferencia_acum_live = acum_keys - live_keys

print("=== RE-EVALUACIÓN CON DNI NORMALIZADO NUMÉRICAMENTE ===")
print(f"Marcaciones en biométrico (Live): {len(live_keys)}")
print(f"Marcaciones en Acumuladas: {len(acum_keys)}")
print(f"Coincidencias EXACTAS 1:1: {len(live_keys.intersection(acum_keys))}")
print(f"En Acumuladas que no estén en Live: {len(diferencia_acum_live)}")
print(f"En Live que no están en Acumuladas: {len(diferencia_live_acum)}")
