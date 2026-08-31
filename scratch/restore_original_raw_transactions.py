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

print(f"Total de marcaciones reales recuperadas de la DB (17 al 22 de Agosto): {len(df_db)}")

print("\n--- VALORES REALES DE CADA COLUMNA (SIN INVENTAR NADA) ---")
print("Tipo de pase de tarjeta:", df_db['Tipo de pase de tarjeta'].value_counts().to_dict())
print("Método de verificación:", df_db['Método de verificación'].value_counts().to_dict())
print("Departamento:", df_db['Departamento'].value_counts().to_dict())
print("Posición:", df_db['Posición'].value_counts().to_dict())

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")
guardar_transacciones_acumuladas_excel(df_db, ruta_acumuladas)

print(f"\nTransacciones_Acumuladas.xlsx RESTAURADO CON LA DATA REAL DE HIKVISION ({len(df_db)} marcaciones).")
