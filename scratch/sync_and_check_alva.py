import sys, os
sys.path.insert(0, os.getcwd())
import pandas as pd
from data.database import sincronizar_aprobaciones_desde_asistencia, get_connection

print("Sincronizando base de datos SQLite con el nuevo motor de asistencia...")
sincronizar_aprobaciones_desde_asistencia()

conn = get_connection()
df_ap = pd.read_sql_query("SELECT * FROM aprobaciones WHERE dni LIKE '%47034929%'", conn)
print("\n=== REGISTRO EN BASE DE DATOS SQLITE PARA JHON ALVA ===")
print(df_ap[['fecha', 'dni', 'apellidos', 'nombres', 'entrada', 'salida', 'horas_trabajadas', 'exceso_jornada_hhmm', 'estado']].to_string())
conn.close()
