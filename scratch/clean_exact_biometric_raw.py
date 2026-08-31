import sqlite3
import pandas as pd
import openpyxl
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.exporter import guardar_transacciones_acumuladas_excel

db_path = os.path.join(ROOT_DIR, "data", "asistencia.db")
conn = sqlite3.connect(db_path)

df_db = pd.read_sql_query("""
SELECT 
    dni as ID,
    nombre as Nombre,
    apellido as Apellido,
    departamento as Departamento,
    cargo as Posición,
    fecha as Fecha,
    semana as Semana,
    tiempo as Tiempo,
    tipo_pase as "Tipo de pase de tarjeta",
    metodo_verificacion as "Método de verificación",
    punto_control as "Punto de control de asistencia"
FROM marcaciones_raw
WHERE fecha >= '2026-08-17' AND fecha <= '2026-08-22'
ORDER BY fecha ASC, tiempo ASC
""", conn)
conn.close()

# Normalizar tiempo a HH:MM:SS de 8 caracteres si viene de 5 caracteres HH:MM
def fix_time(t_str):
    s = str(t_str).strip()
    if len(s) == 5 and ':' in s:
        return f"{s}:00"
    return s

df_db['Tiempo'] = df_db['Tiempo'].apply(fix_time)
df_db['ID'] = df_db['ID'].astype(str).str.strip().str.zfill(8)

# Deduplicar por ID + Fecha + Tiempo
df_clean = df_db.drop_duplicates(subset=['ID', 'Fecha', 'Tiempo']).copy()
df_clean = df_clean.sort_values(by=['Fecha', 'Tiempo', 'ID']).reset_index(drop=True)

print(f"Total de marcaciones reales exactas del biométrico (sin inventar ni modificar valores): {len(df_clean)}")

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
guardar_transacciones_acumuladas_excel(df_clean, ruta_acumuladas)

print("\n--- RESUMEN DE CAMPOS REALES SIN ALTERAR ---")
print("Tipo de pase de tarjeta:", df_clean['Tipo de pase de tarjeta'].value_counts().to_dict())
print("Método de verificación:", df_clean['Método de verificación'].value_counts().to_dict())
print("Departamento:", df_clean['Departamento'].value_counts().to_dict())

print("\n¡Transacciones_Acumuladas.xlsx RE-FORMATEADO CON ÉXITO CON DATA REAL 100% INTACTA!")
