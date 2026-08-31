import sqlite3
import pandas as pd
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import cargar_datos_excel
from core.attendance_engine import procesar_asistencia_df

conn = sqlite3.connect('data/asistencia.db')
df_trab = pd.read_sql("SELECT * FROM trabajadores", conn)
df_trab.columns = [c.upper() for c in df_trab.columns]

excel_raw = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
_, df_marc, df_he = cargar_datos_excel(excel_raw)

df_asist, df_inc, df_he_out, stats = procesar_asistencia_df(df_trab, df_marc, df_he)

df_jesus = df_asist[df_asist['NOMBRES'].str.contains('JESUS', na=False, case=False)]
print("\n--- RESULTADO ACTUAL ASISTENCIA JESUS GABRIEL ---")
print(df_jesus.to_string())
