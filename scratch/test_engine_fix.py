import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
from core.attendance_engine import procesar_asistencia_df, AttendanceConfig
from data.database import obtener_trabajadores_master
from data.data_loader import parse_hikvision_transaction_file

df_trab = obtener_trabajadores_master()
df_marc = parse_hikvision_transaction_file('downloads/data_cruda/Transacciones_Acumuladas.xlsx')

print(f"Total trab: {len(df_trab)}, Total marcaciones crudas: {len(df_marc)}")

df_asis, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

print("Columnas de df_asis:", list(df_asis.columns))

dnis = ['60876523', '62772089', '72500789', '72909375', '72940901', '73485498']
sub = df_asis[
    (df_asis['DNI'].astype(str).str.zfill(8).isin(dnis)) &
    (df_asis['FECHA'].isin(['2026-08-30', '2026-08-31']))
].sort_values(['FECHA', 'DNI'])

print("\n=== CURRENT ASISTENCIA ROWS ===")
for _, r in sub.iterrows():
    print(dict(r))
