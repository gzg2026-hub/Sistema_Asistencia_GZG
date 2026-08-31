import os
import glob
import pandas as pd

pattern = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter\**\*.xlsx"
files = glob.glob(pattern, recursive=True)

print(f"Buscando en {len(files)} archivos de HikCentral...")

for f in files:
    try:
        df = pd.read_excel(f)
        for idx, r in df.iterrows():
            row_str = " ".join([str(v) for v in r.values])
            if "TIMAN" in row_str.upper() or "75295662" in row_str or "SILVA" in row_str.upper():
                print(f"Encontrado en {os.path.basename(f)}: {row_str}")
    except Exception:
        pass
