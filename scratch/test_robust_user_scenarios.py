import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master
from core.attendance_engine import procesar_asistencia_df
from data.exporter import exportar_asistencia_excel

df_trab = obtener_trabajadores_master()

# Raw swipes for JUAN FERNANDO SANCHEZ MONTERO (70782038) matching the user's screenshot exactly
raw_juan = pd.DataFrame([
    # Lunes 17-Ago
    {'ID': '70782038', 'Nombre': 'JUAN FERNANDO', 'Apellido': 'SANCHEZ MONTERO', 'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones', 'Fecha': '2026-08-17', 'Fecha_Clean': '2026-08-17', 'Tiempo': '12:46:00', 'Hora_Clean': pd.to_datetime('12:46:00').time(), 'Tipo de pase de tarjeta': 'Registro de entrada', 'DNI_STR': '70782038'},
    {'ID': '70782038', 'Nombre': 'JUAN FERNANDO', 'Apellido': 'SANCHEZ MONTERO', 'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones', 'Fecha': '2026-08-17', 'Fecha_Clean': '2026-08-17', 'Tiempo': '18:53:00', 'Hora_Clean': pd.to_datetime('18:53:00').time(), 'Tipo de pase de tarjeta': 'Registrar salida', 'DNI_STR': '70782038'},

    # Martes 18-Ago (Morning half day 6h)
    {'ID': '70782038', 'Nombre': 'JUAN FERNANDO', 'Apellido': 'SANCHEZ MONTERO', 'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones', 'Fecha': '2026-08-18', 'Fecha_Clean': '2026-08-18', 'Tiempo': '06:48:00', 'Hora_Clean': pd.to_datetime('06:48:00').time(), 'Tipo de pase de tarjeta': 'Registro de entrada', 'DNI_STR': '70782038'},
    {'ID': '70782038', 'Nombre': 'JUAN FERNANDO', 'Apellido': 'SANCHEZ MONTERO', 'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones', 'Fecha': '2026-08-18', 'Fecha_Clean': '2026-08-18', 'Tiempo': '12:55:00', 'Hora_Clean': pd.to_datetime('12:55:00').time(), 'Tipo de pase de tarjeta': 'Registrar salida', 'DNI_STR': '70782038'},

    # Martes 18-Ago (Evening entry for regular Night shift)
    {'ID': '70782038', 'Nombre': 'JUAN FERNANDO', 'Apellido': 'SANCHEZ MONTERO', 'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones', 'Fecha': '2026-08-18', 'Fecha_Clean': '2026-08-18', 'Tiempo': '18:41:00', 'Hora_Clean': pd.to_datetime('18:41:00').time(), 'Tipo de pase de tarjeta': 'Registro de entrada', 'DNI_STR': '70782038'},

    # Miércoles 19-Ago (Morning exit from Tuesday 18-Ago night shift)
    {'ID': '70782038', 'Nombre': 'JUAN FERNANDO', 'Apellido': 'SANCHEZ MONTERO', 'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones', 'Fecha': '2026-08-19', 'Fecha_Clean': '2026-08-19', 'Tiempo': '07:01:00', 'Hora_Clean': pd.to_datetime('07:01:00').time(), 'Tipo de pase de tarjeta': 'Registrar salida', 'DNI_STR': '70782038'},
])

print("=== RAW INPUT SWIPES ===")
print(raw_juan[['Fecha_Clean', 'Tiempo', 'Tipo de pase de tarjeta']])

print("=== RUNNING ENGINE PROCESSOR FOR JUAN FERNANDO SANCHEZ MONTERO ===")
df_asis, df_he_out, df_inc, _ = procesar_asistencia_df(df_trab, raw_juan)

juan_rows = df_asis[df_asis['DNI'] == '70782038']
print(f"Total rows for Juan Fernando: {len(juan_rows)}")
print(juan_rows[['FECHA', 'TURNO', 'ENTRADA', 'SALIDA', 'HORAS TRABAJADAS', 'INCIDENCIAS']])

excel_bytes = exportar_asistencia_excel(df_trab, raw_juan, df_asis, df_he_out, df_inc)
test_out_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\Reporte_Prueba_70782038.xlsx"
with open(test_out_path, "wb") as f:
    f.write(excel_bytes)

print("\nSaved formatted Excel to:", test_out_path)
