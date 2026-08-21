import pandas as pd

raw_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Informacion_Personal_Raw_2026-08-20.xlsx"
df_raw = pd.read_excel(raw_path, skiprows=6)
print("Columnas:", df_raw.columns.tolist())
match = df_raw[df_raw.iloc[:, 0].astype(str).str.contains('46181231', na=False)]
print("\nBúsqueda Moncada 46181231:")
print(match.to_string())
