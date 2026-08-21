import os
import sys
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

raw_trans = os.path.join(PROJECT_ROOT, "downloads", "data_cruda", "Transacciones_2026-08-17_2026-08-20.xlsx")
df_marc = pd.read_excel(raw_trans)

match = df_marc[df_marc['Apellido'].astype(str).str.contains('CELEN', na=False) | df_marc['Nombre'].astype(str).str.contains('ISAAC', na=False)]
print("=== MARCACIONES RAW CELEN RUIZ ISAAC ===")
print(match[['ID', 'Nombre', 'Apellido', 'Fecha', 'Tiempo', 'Tipo de pase de tarjeta']].to_string())
