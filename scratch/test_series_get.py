import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_datos_db

_, df_marc, _, _, _ = obtener_datos_db()

dni_col = 'ID' if 'ID' in df_marc.columns else ('DNI' if 'DNI' in df_marc.columns else df_marc.columns[0])
df_marc['DNI_STR'] = df_marc[dni_col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

tipo_col = 'Tipo de pase de tarjeta' if 'Tipo de pase de tarjeta' in df_marc.columns else ('TIPO' if 'TIPO' in df_marc.columns else df_marc.columns[-1])

print("tipo_col detected:", repr(tipo_col))
print("Columns in df_marc:", df_marc.columns.tolist())

s_18 = df_marc[(df_marc['DNI_STR'] == '48790853') & (df_marc['Fecha'] == '2026-08-18')]
for _, r in s_18.iterrows():
    print("r.get(tipo_col):", repr(r.get(tipo_col)))
