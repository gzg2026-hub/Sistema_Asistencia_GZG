import sys
import os
sys.path.insert(0, r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG")

import pandas as pd
from data.database import cargar_datos_procesados
from core.attendance_engine import procesar_asistencia

db_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\asistencia.db"
df_trans, df_workers, df_schedules = cargar_datos_procesados(db_path)

# Filtrar para DNI 46671923
dni_target = "46671923"
print(f"=== INFORMACION DE TRABAJADOR DNI {dni_target} ===")
worker_row = df_workers[df_workers['DNI'].astype(str).str.strip() == dni_target]
print(worker_row.to_dict(orient='records'))

print(f"\n=== TRANSACCIONES CRUDAS DE DNI {dni_target} ===")
trans_target = df_trans[df_trans['DNI'].astype(str).str.strip() == dni_target]
print(trans_target.sort_values(by=['FECHA', 'HORA']).to_string())

print(f"\n=== RESULTADO PROCESADO ASISTENCIA ===")
df_asist, df_he, df_inc = procesar_asistencia(df_trans, df_workers, df_schedules)
res_huayama = df_asist[df_asist['DNI'].astype(str).str.strip() == dni_target]
print(res_huayama[['FECHA', 'DNI', 'NOMBRES', 'ENTRADA', 'SALIDA', 'HORAS DE TURNO (HH:MM)', 'EXCESO DE TURNO (HH:MM)', 'HORAS EXTRAS (HH:MM)', 'TOTAL DE HORAS ADICIONALES (HH:MM)', 'TIPO_REGISTRO', 'INCIDENCIAS']].to_string())
