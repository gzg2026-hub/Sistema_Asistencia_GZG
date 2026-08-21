import pandas as pd

raw_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Informacion_Personal_Raw_2026-08-20.xlsx"
df_raw = pd.read_excel(raw_path)
print(f"Total filas en Raw: {len(df_raw)}")
print(df_raw.head(20).to_string())
