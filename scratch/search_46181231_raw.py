import os
import pandas as pd

raw_personal = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Informacion_Personal_Raw_2026-08-20.xlsx"
df_raw = pd.read_excel(raw_personal)

print("Columnas:", df_raw.columns.tolist())
match = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains('46181231', na=False)).any(axis=1)]
print("\nBúsqueda 46181231 en Personal Raw:")
print(match.to_string())

raw_trans = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_2026-08-17_2026-08-20_225331.xlsx"
df_trans = pd.read_excel(raw_trans)
match_t = df_trans[df_trans['ID'].astype(str).str.contains('46181231', na=False)]
print("\nBúsqueda 46181231 en Transacciones Raw:")
print(match_t[['ID', 'Nombre', 'Apellido', 'Fecha', 'Tiempo', 'Tipo de pase de tarjeta']].to_string())
