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

print("=== ACTUALIZANDO CARGO DE JOSE ORLANDO MONCADA REJAS A 'Ingeniero Metalurgico' ===")

dni_moncada = "46181231"
nuevo_cargo = "Ingeniero Metalurgico" # Sin tilde

# 1. Actualizar en Base de Datos SQLite (asistencia.db)
db_path = "data/asistencia.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE trabajadores SET cargo = ? WHERE dni = ?", (nuevo_cargo, dni_moncada))
    c.execute("UPDATE marcaciones_raw SET cargo = ? WHERE dni = ?", (nuevo_cargo, dni_moncada))
    conn.commit()
    conn.close()
    print("Éxito: Padrón de trabajadores y marcaciones_raw actualizados en SQLite.")

# 2. Actualizar en Transacciones_Acumuladas.xlsx
excel_path = "downloads/data_cruda/Transacciones_Acumuladas.xlsx"
if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    dni_col = 'ID' if 'ID' in df.columns else 'DNI'
    pos_col = 'Posición' if 'Posición' in df.columns else ('Posicion' if 'Posicion' in df.columns else 'Cargo')
    
    if dni_col in df.columns and pos_col in df.columns:
        mask = df[dni_col].astype(str).str.strip().str.zfill(8) == dni_moncada
        df.loc[mask, pos_col] = nuevo_cargo
        df.to_excel(excel_path, index=False)
        print(f"Éxito: {mask.sum()} filas actualizadas en Transacciones_Acumuladas.xlsx.")
