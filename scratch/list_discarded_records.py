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
    digits = ''.join(c for c in s if c.isdigit())
    if digits:
        return str(int(digits))
    return s

df_live_raw['clean_id'] = df_live_raw['DNI'].apply(clean_dni)
df_live_raw['clean_fecha'] = df_live_raw['FECHA'].astype(str).str.strip()
df_live_raw['clean_hora'] = df_live_raw['HORA'].astype(str).str.strip()
df_live_raw['key'] = df_live_raw['clean_id'] + "_" + df_live_raw['clean_fecha'] + "_" + df_live_raw['clean_hora']

df_acum['clean_id'] = df_acum['ID'].apply(clean_dni)
df_acum['clean_fecha'] = df_acum['Fecha'].astype(str).str.strip()
df_acum['clean_hora'] = df_acum['Tiempo'].astype(str).str.strip()
df_acum['key'] = df_acum['clean_id'] + "_" + df_acum['clean_fecha'] + "_" + df_acum['clean_hora']

acum_keys = set(df_acum['key'])

# Encontrar los registros de la descarga de Hikvision que no están en Acumuladas
discarded = df_live_raw[~df_live_raw['key'].isin(acum_keys)]

print(f"=== ANÁLISIS DETALLADO DE LOS {len(discarded)} REGISTROS DESCARTADOS ===")
print("Columnas de descartados:", discarded.columns.tolist())

# Mostrar la lista completa de descartados
for idx, r in discarded.iterrows():
    print(f"DNI: {r['clean_id']} | Persona: {r.get('NOMBRES', '')} {r.get('APELLIDOS', '')} | Fecha: {r['clean_fecha']} | Hora: {r['clean_hora']} | Tipo: {r.get('TIPO', '')}")

print("\n--- RESUMEN POR TRABAJADOR Y MOTIVO ---")
print(discarded.groupby(['clean_id', 'NOMBRES', 'APELLIDOS']).size().reset_index(name='Veces_Repetido'))
