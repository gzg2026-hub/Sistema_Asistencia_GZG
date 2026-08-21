import os
import sys
import pandas as pd
from datetime import datetime, time

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import get_connection

conn = get_connection(os.path.join(PROJECT_ROOT, "data", "asistencia.db"))
df_trab = pd.read_sql_query("SELECT dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES, cargo as CARGO, area as ÁREA FROM trabajadores", conn)
conn.close()

raw_path = os.path.join(PROJECT_ROOT, "downloads", "data_cruda", "Transacciones_2026-08-17_2026-08-20.xlsx")
df_marc = pd.read_excel(raw_path)

print(f"Total Trabajadores: {len(df_trab)}, Total Marcaciones: {len(df_marc)}")

# Probar marcaciones raw para los 4 casos clave
target_dnis = {
    '47783594': 'JHON ROBERT AGREDA ASPAJO',
    '03208053': 'FRANCO MORETO BERMEO',
    '006616501': 'YENKLI ORDOÑEZ ARTEAGA',
    '6616501': 'YENKLI ORDOÑEZ ARTEAGA',
    '41219221': 'JOSE ISMAEL VIGO RAFAEL'
}

for dni, nombre in target_dnis.items():
    sub = df_marc[df_marc['ID'].astype(str).str.contains(dni, na=False)]
    if not sub.empty:
        print(f"\n--- {nombre} ({dni}) ---")
        print(sub[['Fecha', 'Tiempo', 'Tipo de pase de tarjeta']].to_string(index=False))
