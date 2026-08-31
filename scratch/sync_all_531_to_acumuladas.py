import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file, fusionar_y_deduplicar_data_cruda
from data.exporter import guardar_transacciones_acumuladas_excel

ruta_live = os.path.join(ROOT_DIR, "downloads", "hikvision", "Transacciones_2026-08-17_2026-08-22.xlsx")
df_live_raw = pd.read_excel(ruta_live, sheet_name=0)

# Mapear columnas al formato oficial
mapping = {
    'DNI': 'ID',
    'NOMBRES': 'Nombre',
    'APELLIDOS': 'Apellido',
    'FECHA': 'Fecha',
    'HORA': 'Tiempo',
    'DISPOSITIVO': 'Punto de control de asistencia',
    'TIPO': 'Tipo de pase de tarjeta'
}
df_live_mapped = df_live_raw.rename(columns=mapping)
if 'Departamento' not in df_live_mapped.columns:
    df_live_mapped['Departamento'] = 'MINA'
if 'Posición' not in df_live_mapped.columns:
    df_live_mapped['Posición'] = 'OPERATIVO'
if 'Semana' not in df_live_mapped.columns:
    df_live_mapped['Semana'] = 'Semana 34'
if 'Método de verificación' not in df_live_mapped.columns:
    df_live_mapped['Método de verificación'] = 'Rostro'

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")

df_master = fusionar_y_deduplicar_data_cruda(df_live_mapped, ruta_acumuladas)
guardar_transacciones_acumuladas_excel(df_master, ruta_acumuladas)

print("=== ACTUALIZACION COMPLETA REALIZADA ===")
print(f"Total marcaciones en Transacciones_Acumuladas.xlsx ahora: {len(df_master)}")
