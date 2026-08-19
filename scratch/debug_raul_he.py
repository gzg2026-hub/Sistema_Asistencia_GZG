import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_datos_db
from core.attendance_engine import parse_date_val, parse_time_val

_, df_marc, _, _, _ = obtener_datos_db("2026-08-17", "2026-08-18")

dni_col = 'ID' if 'ID' in df_marc.columns else 'DNI'
date_col = 'Fecha' if 'Fecha' in df_marc.columns else 'FECHA'

df_marc['DNI_STR'] = df_marc[dni_col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
df_marc['Fecha_Clean'] = df_marc[date_col].apply(parse_date_val)

sample = df_marc[(df_marc['DNI_STR'] == '44955960') & (df_marc['Fecha_Clean'] == '2026-08-17')]
print("--- MARCACIONES RAW DE ESPINOZA SAAVEDRA (44955960) EL 2026-08-17 ---")
for _, r in sample.iterrows():
    tipo_pase = str(r.get('Tipo de pase de tarjeta', '')).strip()
    print(f"Hora: {r.get('Tiempo')} | Tipo Pase: '{tipo_pase}' (repr: {repr(tipo_pase)})")
