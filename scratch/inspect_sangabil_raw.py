import sqlite3
import os
import pandas as pd

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db"
conn = sqlite3.connect(db_path)

query = "SELECT dni, fecha, tiempo, tipo_pase, metodo_verificacion FROM marcaciones_raw WHERE dni LIKE '%48790853%' ORDER BY tiempo;"
df = pd.read_sql_query(query, conn)
print("--- MARCACIONES DE GUERRA SAJAMI SANGABIL (48790853) ---")
print(df.to_string())
