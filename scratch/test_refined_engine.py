import os
import sys
import pandas as pd
from datetime import datetime, time, timedelta

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from core.attendance_engine import parse_date_val, parse_time_val, time_to_seconds

# Raw file path
raw_path = os.path.join(PROJECT_ROOT, "downloads", "data_cruda", "Transacciones_2026-08-17_2026-08-20.xlsx")
df_raw = pd.read_excel(raw_path)

print(f"Total marcaciones en data cruda: {len(df_raw)}")

# Inspeccionar Ivan Antonio Vasquez Puelles (48455175)
df_ivan = df_raw[df_raw['ID'].astype(str).str.contains('48455175', na=False)]
print("\n--- MARCACIONES RAW DE IVAN ANTONIO VASQUEZ PUELLES (48455175) ---")
print(df_ivan[['ID', 'Nombre', 'Apellido', 'Fecha', 'Tiempo', 'Tipo de pase de tarjeta']].to_string(index=False))

# Inspeccionar Luis Fernando Ramirez Guerrero (70088280)
df_luis = df_raw[df_raw['ID'].astype(str).str.contains('70088280', na=False)]
print("\n--- MARCACIONES RAW DE LUIS FERNANDO RAMIREZ GUERRERO (70088280) ---")
print(df_luis[['ID', 'Nombre', 'Apellido', 'Fecha', 'Tiempo', 'Tipo de pase de tarjeta']].to_string(index=False))
