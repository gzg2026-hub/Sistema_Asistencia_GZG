import sqlite3
import pandas as pd

excel_path = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter\Información personal_2026_08_20_09_43_12_084\Información personal_2026_08_20_09_43_12_084.xlsx"
db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"

# 1. Leer Excel oficial de los 54 trabajadores
df_raw = pd.read_excel(excel_path, skiprows=7)
df_raw.rename(columns={
    'ID': 'DNI',
    'Nombre': 'NOMBRES',
    'Apellido': 'APELLIDOS',
    'Departamento': 'AREA',
    'Posición': 'CARGO',
    'Posicin': 'CARGO'
}, inplace=True)

def clean_area(val):
    val_str = str(val).strip()
    if '>' in val_str:
        val_str = val_str.split('>')[-1].strip()
    if '/' in val_str:
        val_str = val_str.split('/')[-1].strip()
    return val_str

df_raw['DNI'] = df_raw['DNI'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
df_raw['AREA'] = df_raw['AREA'].apply(clean_area)
df_raw['CARGO'] = df_raw['CARGO'].fillna('').astype(str).str.strip()

print(f"Total personas en Excel oficial del biométrico: {len(df_raw)}")

# 2. Reemplazar la tabla 'trabajadores' en SQLite para que tenga EXACTAMENTE las 54 personas
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Limpiar la tabla trabajadores
cursor.execute("DELETE FROM trabajadores;")

for _, row in df_raw.iterrows():
    dni = str(row['DNI']).strip()
    if not dni or dni.lower() == 'nan':
        continue
    apellidos = str(row.get('APELLIDOS', '')).strip()
    nombres = str(row.get('NOMBRES', '')).strip()
    cargo = str(row.get('CARGO', '')).strip()
    area = str(row.get('AREA', '')).strip()
    
    cursor.execute("""
    INSERT INTO trabajadores (dni, apellidos, nombres, cargo, area, updated_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (dni, apellidos, nombres, cargo, area))

conn.commit()

# Verificación
count = cursor.execute("SELECT COUNT(*) FROM trabajadores;").fetchone()[0]
conn.close()

print(f"[OK] Se sincronizó la tabla 'trabajadores'. Total personas activas en la BD: {count}")
