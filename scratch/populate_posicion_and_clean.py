import os
import pandas as pd
import sqlite3

def quitar_tildes(texto: str) -> str:
    if not isinstance(texto, str) or not texto or str(texto).strip().lower() in ('nan', 'none', ''):
        return ""
    replacements = {
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U',
        'á': 'A', 'é': 'E', 'í': 'I', 'ó': 'O', 'ú': 'U', 'ü': 'U',
        'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
        'à': 'A', 'è': 'E', 'ì': 'I', 'ò': 'O', 'ù': 'U',
    }
    res = str(texto)
    for k, v in replacements.items():
        res = res.replace(k, v)
    return res.strip()

print("=== ACTUALIZANDO POSICION / CARGO Y LIMPIANDO TILDES EN TRANSACCIONES ACUMULADAS ===")

db_path = "data/asistencia.db"
cargo_map = {}
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute("SELECT dni, cargo FROM trabajadores").fetchall()
    for dni_val, cargo_val in rows:
        if dni_val and cargo_val:
            dni_clean = str(dni_val).strip().zfill(8)
            cargo_map[dni_clean] = str(cargo_val).strip()
    conn.close()

excel_path = "downloads/data_cruda/Transacciones_Acumuladas.xlsx"
if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    
    # 1. Limpiar tildes en Nombres y Apellidos
    for col in ['Nombre', 'Apellido', 'Nombres', 'Apellidos']:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(quitar_tildes)

    # 2. Formatear ID / DNI como texto de 8 dígitos
    for col_dni in ['ID', 'DNI']:
        if col_dni in df.columns:
            df[col_dni] = df[col_dni].astype(str).str.strip().str.zfill(8)

    # 3. Poblar Posición / Cargo desde el mapa si está vacío
    dni_col = 'ID' if 'ID' in df.columns else 'DNI'
    pos_col = 'Posición' if 'Posición' in df.columns else ('Posicion' if 'Posicion' in df.columns else 'Cargo')
    
    if pos_col not in df.columns:
        df['Posición'] = ""
        pos_col = 'Posición'

    updated_count = 0
    for idx, row in df.iterrows():
        d_val = str(row.get(dni_col, '')).strip().zfill(8)
        current_pos = str(row.get(pos_col, '')).strip()
        if (not current_pos or current_pos.lower() in ('nan', 'none', '', '-')) and d_val in cargo_map:
            df.loc[idx, pos_col] = cargo_map[d_val]
            updated_count += 1

    df.to_excel(excel_path, index=False)
    print(f"Éxito: Transacciones_Acumuladas.xlsx actualizado. Se completaron {updated_count} posiciones vacías.")
