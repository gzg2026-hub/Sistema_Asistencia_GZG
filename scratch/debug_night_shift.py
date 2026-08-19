import sys
import os
import pandas as pd
from datetime import datetime, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_datos_db
from core.attendance_engine import parse_date_val, parse_time_val, time_to_seconds, AttendanceConfig

_, df_marc, _, _, _ = obtener_datos_db()

dni_col = 'ID' if 'ID' in df_marc.columns else 'DNI'
df_marc['DNI_STR'] = df_marc[dni_col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
df_marc['Fecha_Clean'] = df_marc['Fecha'].apply(parse_date_val)
df_marc['Hora_Clean'] = df_marc['Tiempo'].apply(parse_time_val)

tipo_col = 'Tipo de pase de tarjeta'
fecha = '2026-08-17'
dni = '48790853'
dni_clean = '48790853'
entrada = parse_time_val('18:50')
salida = None
config = AttendanceConfig()

print("Ejecutando bloque de salida nocturna...")
try:
    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
    fecha_next_str = (fecha_dt + timedelta(days=1)).strftime('%Y-%m-%d')
    print("fecha_next_str:", fecha_next_str)
    
    next_day_swipes = df_marc[
        (df_marc['DNI_STR'].apply(lambda d: str(d).strip().lstrip('0')) == dni_clean) &
        (df_marc['Fecha_Clean'] == fecha_next_str)
    ]
    print("Total rows en next_day_swipes:", len(next_day_swipes))
    
    salida_next_rows = [
        r for _, r in next_day_swipes.iterrows()
        if 'salida' in str(r.get(tipo_col, '')).strip().lower() and not ('horas extra' in str(r.get(tipo_col, '')).strip().lower() or 'he' in str(r.get(tipo_col, '')).strip().lower())
        and r['Hora_Clean'] is not None and time_to_seconds(r['Hora_Clean']) <= 43200
    ]
    print("salida_next_rows:", salida_next_rows)
    if salida_next_rows:
        salida_next_rows.sort(key=lambda r: time_to_seconds(r['Hora_Clean']))
        salida = salida_next_rows[0]['Hora_Clean']
        print("EXITO SALIDA ENCONTRADA:", salida)
except Exception as e:
    import traceback
    print("ERROR EXCEPCION:", e)
    print(traceback.format_exc())
