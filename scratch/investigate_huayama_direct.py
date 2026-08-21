import sys
import os
sys.path.insert(0, r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG")

import pandas as pd
from core.data_loader import cargar_datos_excel
from core.attendance_engine import procesar_asistencia_df

excel_crudo = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_2026-08-17_2026-08-21_121032.xlsx"
excel_pers = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Personal_Asistencia_GZG.xlsx"

df_trans, df_workers, df_schedules = cargar_datos_excel(excel_crudo, excel_pers)

dni_target = "46671923"
print(f"=== INFORMACION DE TRABAJADOR DNI {dni_target} ===")
worker_row = df_workers[df_workers['DNI'].astype(str).str.strip() == dni_target]
print(worker_row.to_dict(orient='records'))

print(f"\n=== TRANSACCIONES CRUDAS DE DNI {dni_target} ===")
trans_target = df_trans[df_trans['DNI'].astype(str).str.strip() == dni_target]
print(trans_target.sort_values(by=['FECHA', 'HORA']).to_string())

df_asist, df_he, df_inc, stats = procesar_asistencia_df(df_workers, df_trans)
res_huayama = df_asist[df_asist['DNI'].astype(str).str.strip() == dni_target]

print(f"\n=== RESULTADO PROCESADO DE DNI {dni_target} ===")
for idx, r in res_huayama.iterrows():
    print(f"Fecha: {r.get('FECHA')} | Turno: {r.get('TURNO')} | Ent: {r.get('ENTRADA')} | Sal: {r.get('SALIDA')} | Horas Turno: {r.get('HORAS DE TURNO (HH:MM)')} | Exceso Turno: {r.get('EXCESO DE TURNO (HH:MM)')} | Tipo: {r.get('TIPO_REGISTRO')} | Obs: {r.get('INCIDENCIAS')}")
