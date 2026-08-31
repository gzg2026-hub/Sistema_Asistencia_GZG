import pandas as pd
import sqlite3
import os

padron_path = 'Padron_Trabajadores_GZG.xlsx'
if os.path.exists(padron_path):
    df_padron = pd.read_excel(padron_path)
    print("Columnas en Padron:", df_padron.columns.tolist())
    match = df_padron[df_padron.astype(str).apply(lambda r: r.str.contains('72559194|Riva', case=False).any(), axis=1)]
    print("\nFila de Javier en Padron:")
    print(match.to_dict(orient='records'))

conn = sqlite3.connect('data/asistencia.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM trabajadores WHERE dni = '72559194'")
print("\nTrabajadores en DB:", cursor.fetchall())
cursor.execute("SELECT * FROM usuarios WHERE username = 'jdelariva'")
print("\nUsuario jdelariva en DB:", cursor.fetchall())
conn.close()
