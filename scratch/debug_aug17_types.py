import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_datos_db

_, df_marc, _, _, _ = obtener_datos_db("2026-08-17", "2026-08-18")

df_17 = df_marc[df_marc['Fecha'].astype(str).str.contains('2026-08-17')]
print(df_17['Tipo de pase de tarjeta'].value_counts(dropna=False))
