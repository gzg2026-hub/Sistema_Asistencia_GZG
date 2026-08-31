import pandas as pd
import openpyxl
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.data_loader import parse_hikvision_transaction_file

ruta_acumuladas = os.path.join(ROOT_DIR, "downloads", "data_cruda", "Transacciones_Acumuladas.xlsx")

print("--- AUDITORIA PROFUNDA DE TRANSACCIONES_ACUMULADAS.XLSX ---")
print(f"Ruta: {ruta_acumuladas}\n")

if not os.path.exists(ruta_acumuladas):
    print("ERROR CRITICO: El archivo Transacciones_Acumuladas.xlsx no existe!")
    sys.exit(1)

df = parse_hikvision_transaction_file(ruta_acumuladas)

print("1. ESTRUCTURA GENERAL:")
print(f"   - Total de Filas: {len(df)}")
print(f"   - Total de Columnas: {len(df.columns)}")
print(f"   - Columnas Presentes: {df.columns.tolist()}")

col_oficiales = [
    'ID', 'Nombre', 'Apellido', 'Departamento', 'Posición',
    'Fecha', 'Semana', 'Tiempo', 'Tipo de pase de tarjeta',
    'Método de verificación', 'Punto de control de asistencia'
]

es_orden_exacto = (df.columns.tolist() == col_oficiales)
print(f"   - Orden de 11 columnas oficial 100% exacto: {es_orden_exacto}")

print("\n2. RANGO DE FECHAS Y DIAS PROCESADOS:")
if 'Fecha' in df.columns:
    fechas = sorted(df['Fecha'].dropna().unique().tolist())
    print(f"   - Fechas encontradas ({len(fechas)} dias): {fechas}")
    min_f = min(fechas) if fechas else "-"
    max_f = max(fechas) if fechas else "-"
    print(f"   - Periodo cubierto: Desde {min_f} Hasta {max_f}")

print("\n3. INTEGRIDAD DE TRABAJADORES:")
if 'ID' in df.columns:
    ids_unicos = df['ID'].astype(str).unique()
    print(f"   - Cantidad de IDs / Trabajadores Unicos: {len(ids_unicos)}")

if 'Nombre' in df.columns and 'Apellido' in df.columns:
    nombres_unicos = (df['Nombre'].fillna('') + " " + df['Apellido'].fillna('')).unique()
    print(f"   - Cantidad de Nombres Unicos: {len(nombres_unicos)}")

print("\n4. VERIFICACION DE DUPLICADOS Y VALORES NULOS:")
num_duplicados = df.duplicated().sum()
print(f"   - Filas Duplicadas Identificadas: {num_duplicados}")
null_ids = df['ID'].isna().sum() if 'ID' in df.columns else 0
null_fechas = df['Fecha'].isna().sum() if 'Fecha' in df.columns else 0
null_tiempos = df['Tiempo'].isna().sum() if 'Tiempo' in df.columns else 0
print(f"   - Nulos en ID: {null_ids} | Nulos en Fecha: {null_fechas} | Nulos en Tiempo: {null_tiempos}")

print("\n5. VERIFICACION DE TRABAJADORES CLAVE Y SUS MARCACIONES:")
trabajadores_clave = {
    '62772089': 'JESUS GABRIEL LADINES AGURTO',
    '70782038': 'JUAN FERNANDO SANCHEZ MONTERO',
    '71060137': 'HILDEBRANDO RAMIREZ LABAN'
}

for dni, nombre in trabajadores_clave.items():
    sub = df[df['ID'].astype(str).str.contains(dni, na=False)]
    print(f"\n   -> {nombre} (DNI {dni}): {len(sub)} marcaciones encontradas")
    if not sub.empty and 'Fecha' in sub.columns and 'Tiempo' in sub.columns:
        for f, group in sub.groupby('Fecha'):
            t_list = group['Tiempo'].tolist()
            tipo_list = group['Tipo de pase de tarjeta'].tolist() if 'Tipo de pase de tarjeta' in group.columns else []
            punto_list = group['Punto de control de asistencia'].tolist() if 'Punto de control de asistencia' in group.columns else []
            print(f"       * {f}: {len(group)} marcacion(es) -> {list(zip(t_list, tipo_list, punto_list))}")

print("\n=== FIN DE AUDITORIA DE DATA CRUDA ===")
