import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master
from core.attendance_engine import procesar_asistencia_df

df_trab = obtener_trabajadores_master()

# Simular marcaciones de Cesar Rimarachin (77386038)
# CASO 1: Solo marcaciones del día 18-Ago (entrada 18:31, y salida 07:00 de la mañana del 18)
raw_18_only = pd.DataFrame([
    {
        'ID': '77386038', 'Nombre': 'CESAR', 'Apellido': 'RIMARACHIN GARCIA',
        'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones',
        'Fecha': '2026-08-18', 'Fecha_Clean': '2026-08-18',
        'Tiempo': '07:00:00', 'Hora_Clean': pd.to_datetime('07:00:00').time(),
        'Tipo de pase de tarjeta': 'Registrar salida', 'DNI_STR': '77386038'
    },
    {
        'ID': '77386038', 'Nombre': 'CESAR', 'Apellido': 'RIMARACHIN GARCIA',
        'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones',
        'Fecha': '2026-08-18', 'Fecha_Clean': '2026-08-18',
        'Tiempo': '18:31:00', 'Hora_Clean': pd.to_datetime('18:31:00').time(),
        'Tipo de pase de tarjeta': 'Registro de entrada', 'DNI_STR': '77386038'
    }
])

# CASO 2: Marcaciones del día 18-Ago + 19-Ago (salida 05:01 de la mañana del 19)
raw_18_and_19 = pd.DataFrame([
    {
        'ID': '77386038', 'Nombre': 'CESAR', 'Apellido': 'RIMARACHIN GARCIA',
        'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones',
        'Fecha': '2026-08-18', 'Fecha_Clean': '2026-08-18',
        'Tiempo': '07:00:00', 'Hora_Clean': pd.to_datetime('07:00:00').time(),
        'Tipo de pase de tarjeta': 'Registrar salida', 'DNI_STR': '77386038'
    },
    {
        'ID': '77386038', 'Nombre': 'CESAR', 'Apellido': 'RIMARACHIN GARCIA',
        'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones',
        'Fecha': '2026-08-18', 'Fecha_Clean': '2026-08-18',
        'Tiempo': '18:31:00', 'Hora_Clean': pd.to_datetime('18:31:00').time(),
        'Tipo de pase de tarjeta': 'Registro de entrada', 'DNI_STR': '77386038'
    },
    {
        'ID': '77386038', 'Nombre': 'CESAR', 'Apellido': 'RIMARACHIN GARCIA',
        'Departamento': 'Oper&Mtto', 'Cargo': 'Operaciones',
        'Fecha': '2026-08-19', 'Fecha_Clean': '2026-08-19',
        'Tiempo': '05:01:00', 'Hora_Clean': pd.to_datetime('05:01:00').time(),
        'Tipo de pase de tarjeta': 'Registrar salida', 'DNI_STR': '77386038'
    }
])

print("--- PROCESANDO CASO 1 (Solo 18-Ago) ---")
df_asis1, _, _, _ = procesar_asistencia_df(df_trab, raw_18_only)
cesar1 = df_asis1[df_asis1['DNI'] == '77386038']
for _, r in cesar1.iterrows():
    print(f"Fecha Entrada: {r.get('FECHA_ENTRADA')} | Hora Entrada: {r.get('ENTRADA')} | Fecha Salida: {r.get('FECHA_SALIDA')} | Hora Salida: {r.get('SALIDA')} | Estado: {r.get('ESTADO')}")

print("\n--- PROCESANDO CASO 2 (18-Ago + 19-Ago hasta la mañana) ---")
df_asis2, _, _, _ = procesar_asistencia_df(df_trab, raw_18_and_19)
cesar2 = df_asis2[df_asis2['DNI'] == '77386038']
for _, r in cesar2.iterrows():
    print(f"Fecha Entrada: {r.get('FECHA_ENTRADA')} | Hora Entrada: {r.get('ENTRADA')} | Fecha Salida: {r.get('FECHA_SALIDA')} | Hora Salida: {r.get('SALIDA')} | Estado: {r.get('ESTADO')}")
