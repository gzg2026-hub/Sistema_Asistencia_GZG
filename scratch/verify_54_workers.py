import sqlite3
import pandas as pd

excel_path = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter\Información personal_2026_08_20_09_43_12_084\Información personal_2026_08_20_09_43_12_084.xlsx"
db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"

# 1. Leer Excel del usuario
df_excel = pd.read_excel(excel_path, skiprows=7)
df_excel.rename(columns={'ID': 'DNI', 'Nombre': 'NOMBRES', 'Apellido': 'APELLIDOS'}, inplace=True)
df_excel['DNI_CLEAN'] = df_excel['DNI'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
excel_dnis = set(df_excel['DNI_CLEAN'].dropna().unique())

print(f"Total filas en Excel del biométrico (manual): {len(df_excel)}")
print(f"Total DNIs únicos en Excel del biométrico: {len(excel_dnis)}")

# 2. Leer SQLite BD
conn = sqlite3.connect(db_path)
df_db = pd.read_sql_query("SELECT dni, apellidos, nombres, cargo, area FROM trabajadores ORDER BY dni", conn)
print(f"\nTotal registros en BD 'trabajadores': {len(df_db)}")

# Buscar DNIs que están en BD pero NO en el Excel oficial del biométrico
db_dnis = set(df_db['dni'].astype(str).str.strip())
extra_in_db = db_dnis - excel_dnis

print("\n--- DNIs EN EXCEL PARA ORDOÑEZ Y MORETO ---")
print(df_excel[df_excel['APELLIDOS'].astype(str).str.contains('ORDO|MORETO', case=False, na=False)][['DNI', 'DNI_CLEAN', 'APELLIDOS', 'NOMBRES']])

print("\n--- DNIs EN BD PARA ORDOÑEZ Y MORETO ---")
print(df_db[df_db['apellidos'].astype(str).str.contains('ORDO|MORETO', case=False, na=False)])

conn.close()
