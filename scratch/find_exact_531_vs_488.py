import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file

ruta_live = os.path.join(ROOT_DIR, "downloads", "hikvision", "Transacciones_2026-08-17_2026-08-22.xlsx")
df_live = pd.read_excel(ruta_live, sheet_name=0)

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
df_acum = parse_hikvision_transaction_file(ruta_acumuladas)

print(f"Total registros brutos en descarga de HikCentral: {len(df_live)}")
print(f"Total registros en Transacciones_Acumuladas.xlsx: {len(df_acum)}")

# Comparar filas en df_live que se consolidan en df_acum
def make_key(df, dni_col, fecha_col, hora_col):
    d = df[dni_col].astype(str).str.strip().str.lstrip('0')
    f = df[fecha_col].astype(str).str.strip()
    h = df[hora_col].astype(str).str.strip()
    return d + "_" + f + "_" + h

df_live['key'] = make_key(df_live, 'DNI', 'FECHA', 'HORA')
df_acum['key'] = make_key(df_acum, 'ID', 'Fecha', 'Tiempo')

dup_in_live = df_live[df_live.duplicated(subset=['key'], keep=False)]
print(f"\n1. Marcaciones DUPLICADAS EN EL MISMO SEGUNDO en HikCentral: {len(dup_in_live)}")
if not dup_in_live.empty:
    print(dup_in_live[['DNI', 'APELLIDOS', 'NOMBRES', 'FECHA', 'HORA']].head(10))

invalid_in_live = df_live[df_live['DNI'].isna() | df_live['FECHA'].isna() | df_live['HORA'].isna()]
print(f"\n2. Marcaciones con datos NULOS o INVALIDOS en HikCentral: {len(invalid_in_live)}")

live_unique_keys = set(df_live['key'].dropna())
acum_unique_keys = set(df_acum['key'].dropna())

diff = live_unique_keys - acum_unique_keys
print(f"\n3. Llaves únicas en Live no presentes en Acumuladas: {len(diff)}")
if diff:
    sample_diff = df_live[df_live['key'].isin(diff)]
    print(sample_diff[['DNI', 'APELLIDOS', 'NOMBRES', 'FECHA', 'HORA', 'TIPO']])
