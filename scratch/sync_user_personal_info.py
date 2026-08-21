import os
import shutil
import sqlite3
import pandas as pd

src_file = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter\Información personal_2026_08_20_09_43_12_084\Información personal_2026_08_20_09_43_12_084.xlsx"
dest_file = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Información personal_2026_08_20_09_43_12_084.xlsx"
db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"

# 1. Copiar a downloads/data_cruda
shutil.copy2(src_file, dest_file)
print(f"Copiado archivo a: {dest_file}")

# 2. Leer Excel encontrando la fila que contiene 'ID'
df_full = pd.read_excel(src_file, header=None)
header_row_idx = None
for idx, row in df_full.iterrows():
    row_vals = [str(x).strip() for x in row.values]
    if 'ID' in row_vals and ('Nombre' in row_vals or 'Apellido' in row_vals):
        header_row_idx = idx
        break

print(f"Header row found at index: {header_row_idx}")
df_raw = pd.read_excel(src_file, skiprows=header_row_idx)
print("Columnas leídas:", list(df_raw.columns))
print("Total trabajadores leídos:", len(df_raw))

# Limpieza de nombres de columna
df_raw.rename(columns={
    'ID': 'DNI',
    'Nombre': 'NOMBRES',
    'Apellido': 'APELLIDOS',
    'Departamento': 'AREA',
    'Posición': 'CARGO',
    'Posicin': 'CARGO'
}, inplace=True)

# Normalizar DNI y Área
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

# 3. Guardar/Actualizar en SQLite DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

updated_count = 0
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
    ON CONFLICT(dni) DO UPDATE SET
        apellidos=excluded.apellidos,
        nombres=excluded.nombres,
        cargo=excluded.cargo,
        area=excluded.area,
        updated_at=CURRENT_TIMESTAMP
    """, (dni, apellidos, nombres, cargo, area))
    updated_count += 1

conn.commit()
conn.close()

print(f"[OK] Se importaron/actualizaron exitosamente {updated_count} trabajadores en la base de datos asistencia.db.")
