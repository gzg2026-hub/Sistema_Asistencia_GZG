import sqlite3
import pandas as pd
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file, cargar_datos_excel
from core.attendance_engine import procesar_asistencia_df

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
excel_padron = os.path.join(ROOT_DIR, "Padron_Trabajadores_GZG.xlsx")

df_trab, _, _ = cargar_datos_excel(excel_padron)
if df_trab.empty:
    conn = sqlite3.connect('data/asistencia.db')
    df_trab = pd.read_sql("SELECT * FROM trabajadores", conn)

df_trab.columns = [c.upper() for c in df_trab.columns]
df_acum = parse_hikvision_transaction_file(ruta_acumuladas)

df_hild_raw = df_acum[df_acum['ID'].astype(str).str.contains('71060137')]
print("\n=== MARCACIONES RAW HILDEBRANDO RAMIREZ ===")
print(df_hild_raw[['ID', 'Fecha', 'Semana', 'Tiempo', 'Tipo de pase de tarjeta', 'Punto de control de asistencia']].to_string())

df_asist, df_inc, df_he, stats = procesar_asistencia_df(df_trab, df_acum)
df_hild_asist = df_asist[df_asist['NOMBRES'].str.contains('HILDEBRANDO', na=False, case=False)]

print("\n=== REPORTE PROCESADO HILDEBRANDO RAMIREZ ===")
print(df_hild_asist[['FECHA', 'TURNO', 'ENTRADA', 'SALIDA', 'HORAS TRABAJADAS', 'ESTADO ASISTENCIA', 'INCIDENCIAS']].to_string())
