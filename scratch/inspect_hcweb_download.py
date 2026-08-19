import os
import glob
import pandas as pd

folder = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter\Transacciones_2026_08_18_22_38_46"
files = glob.glob(os.path.join(folder, "*.xlsx")) + glob.glob(os.path.join(folder, "*.csv"))

print("Archivos en el directorio:", files)
for f in files:
    print(f"\n--- CONTENIDO DE {os.path.basename(f)} ---")
    df = pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f)
    print("Columnas:", list(df.columns))
    print("Total filas:", len(df))
    raul = df[df.astype(str).apply(lambda row: row.str.contains('44955960|ESPINOZA').any(), axis=1)]
    print("\nFilas de Raul Espinoza:")
    print(raul.to_string())
