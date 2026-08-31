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

print("=== REMOVIENDO TILDES DE NOMBRES Y APELLIDOS ===")

# 1. Transacciones_Acumuladas.xlsx
excel_path = "downloads/data_cruda/Transacciones_Acumuladas.xlsx"
if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    for col in ['Nombres', 'Apellidos', 'Nombre', 'Apellido']:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(quitar_tildes)
    
    # Formatear DNI como texto si existe
    for col_dni in ['ID', 'DNI']:
        if col_dni in df.columns:
            df[col_dni] = df[col_dni].astype(str).str.strip().str.zfill(8)
            
    df.to_excel(excel_path, index=False)
    print("Éxito: Transacciones_Acumuladas.xlsx limpiado sin tildes.")

# 2. Base de datos SQLite
db_path = "data/asistencia.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT rowid, nombre, apellido FROM marcaciones_raw")
    rows = cursor.fetchall()
    for rowid, nom, ape in rows:
        clean_nom = quitar_tildes(nom)
        clean_ape = quitar_tildes(ape)
        cursor.execute("UPDATE marcaciones_raw SET nombre = ?, apellido = ? WHERE rowid = ?", (clean_nom, clean_ape, rowid))
        
    cursor.execute("SELECT dni, nombres, apellidos FROM trabajadores")
    t_rows = cursor.fetchall()
    for t_dni, nom, ape in t_rows:
        clean_nom = quitar_tildes(nom)
        clean_ape = quitar_tildes(ape)
        cursor.execute("UPDATE trabajadores SET nombres = ?, apellidos = ? WHERE dni = ?", (clean_nom, clean_ape, t_dni))
        
    conn.commit()
    conn.close()
    print("Éxito: Base de datos asistencia.db limpiada sin tildes.")
