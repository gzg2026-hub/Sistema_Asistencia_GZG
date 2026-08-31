import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file
from data.exporter import guardar_transacciones_acumuladas_excel

ruta_live = os.path.join(ROOT_DIR, "downloads", "hikvision", "Transacciones_2026-08-17_2026-08-22.xlsx")
df_live_raw = pd.read_excel(ruta_live, sheet_name=0)

# Mapear columnas al formato oficial exacto de 11 columnas
df_live_mapped = pd.DataFrame()
df_live_mapped['ID'] = df_live_raw['DNI'].astype(str).str.strip().str.zfill(8)
df_live_mapped['Nombre'] = df_live_raw['NOMBRES'].astype(str).str.strip()
df_live_mapped['Apellido'] = df_live_raw['APELLIDOS'].astype(str).str.strip()
df_live_mapped['Departamento'] = 'MINA'
df_live_mapped['Posición'] = 'OPERATIVO'
df_live_mapped['Fecha'] = df_live_raw['FECHA'].astype(str).str.strip()
df_live_mapped['Semana'] = 'Semana 34'
df_live_mapped['Tiempo'] = df_live_raw['HORA'].astype(str).str.strip()
df_live_mapped['Tipo de pase de tarjeta'] = df_live_raw['TIPO'].astype(str).str.strip()
df_live_mapped['Método de verificación'] = 'Rostro'
df_live_mapped['Punto de control de asistencia'] = df_live_raw['DISPOSITIVO'].astype(str).str.strip()

# Deduplicar exactamente por (ID, Fecha, Tiempo)
df_clean = df_live_mapped.drop_duplicates(subset=['ID', 'Fecha', 'Tiempo']).copy()
df_clean = df_clean.sort_values(by=['Fecha', 'Tiempo', 'ID']).reset_index(drop=True)

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
guardar_transacciones_acumuladas_excel(df_clean, ruta_acumuladas)

print("=== RE-SINCRONIZACIÓN PERFECTA EXECUTADA ===")
print(f"Total marcaciones exactamente guardadas en Transacciones_Acumuladas.xlsx: {len(df_clean)}")
