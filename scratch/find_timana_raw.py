import os
import pandas as pd

raw_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Informacion_Personal_Raw_2026-08-22.xlsx"

df = pd.read_excel(raw_path)
print("Columnas en raw personal:", df.columns)

matches = []
for idx, r in df.iterrows():
    row_str = " ".join([str(v) for v in r.values])
    if "TIMAN" in row_str.upper() or "75295662" in row_str:
        matches.append(r.values)

print(f"Coincidencias para Timana en raw personal ({len(matches)}):")
for m in matches:
    print(" ", m)
