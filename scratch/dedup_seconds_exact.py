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

df_db['ID'] = df_db['ID'].astype(str).str.strip().str.zfill(8)
df_db['Tiempo'] = df_db['Tiempo'].astype(str).str.strip()

# Si existen dos filas para el mismo ID, Fecha y mismo HH:MM, priorizar la que tiene segundos reales != '00'
df_db['hh_mm'] = df_db['Tiempo'].str[:5]
df_db['has_sec'] = df_db['Tiempo'].apply(lambda t: 1 if len(t) == 8 and not t.endswith(':00') else 0)

df_db = df_db.sort_values(by=['Fecha', 'ID', 'hh_mm', 'has_sec'], ascending=[True, True, True, False])
df_clean = df_db.drop_duplicates(subset=['ID', 'Fecha', 'hh_mm'], keep='first').copy()

df_clean = df_clean.drop(columns=['hh_mm', 'has_sec'])
df_clean = df_clean.sort_values(by=['Fecha', 'Tiempo', 'ID']).reset_index(drop=True)

print(f"Total marcaciones deduplicadas limpias con segundos reales: {len(df_clean)}")

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
guardar_transacciones_acumuladas_excel(df_clean, ruta_acumuladas)

print("\n¡Transacciones_Acumuladas.xlsx RE-GUARDADO PERFECTAMENTE CON DATOS REALES DE HIKVISION!")
