import os
import sys
import datetime
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from core.hikvision_downloader import descargar_transacciones_hikvision
from data.database import get_connection, guardar_trabajadores, guardar_marcaciones_raw, guardar_asistencia_y_reportes
from core.attendance_engine import procesar_asistencia_df
from data.exporter import exportar_asistencia_excel

fecha_inicio = "2026-08-17"
fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")

print(f"=== INICIANDO DESCARGA Y PROCESAMIENTO GZG: {fecha_inicio} a {fecha_hoy} ===")

# 1. Sincronizar Padrón de trabajadores en la raíz
padron_path = os.path.join(PROJECT_ROOT, "Padron_Trabajadores_GZG.xlsx")
db_path = os.path.join(PROJECT_ROOT, "data", "asistencia.db")
conn = get_connection(db_path)

if os.path.exists(padron_path):
    df_p = pd.read_excel(padron_path)
    df_p.rename(columns={
        'DNI': 'dni', 'APELLIDOS': 'apellidos', 'NOMBRES': 'nombres',
        'CARGO': 'cargo', 'ÁREA': 'area', 'DEPARTAMENTO': 'area'
    }, inplace=True)
    guardar_trabajadores(df_p, db_path)
    print(f"[Padrón] {len(df_p)} trabajadores actualizados desde {padron_path}")

# 2. Descargar marcaciones crudas 1:1 desde HikCentral
carpeta_raw = os.path.join(PROJECT_ROOT, "downloads", "data_cruda")
raw_excel_path = descargar_transacciones_hikvision(
    carpeta_destino=carpeta_raw,
    fecha_inicio=fecha_inicio,
    fecha_fin=fecha_hoy
)

print(f"[Raw Data] Archivo de transacciones guardado en: {raw_excel_path}")

# 3. Cargar marcaciones descargadas y trabajadores de la DB
df_marc = pd.read_excel(raw_excel_path)
df_trab = pd.read_sql_query("SELECT dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES, cargo as CARGO, area as ÁREA FROM trabajadores", conn)

guardar_marcaciones_raw(df_marc, db_path)

# 4. Procesar Asistencia con todas las reglas de negocio
df_asist, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

guardar_asistencia_y_reportes(df_asist, df_he, df_inc, db_path)

# 5. Exportar reporte procesado Excel
excel_bytes = exportar_asistencia_excel(df_trab, df_marc, df_asist, df_he, df_inc)

carpeta_proc = os.path.join(PROJECT_ROOT, "downloads", "data_procesada")
proc_excel_path = os.path.join(carpeta_proc, f"Reporte_Asistencia_GZG_{fecha_inicio}_al_{fecha_hoy}.xlsx")

try:
    with open(proc_excel_path, "wb") as f:
        f.write(excel_bytes)
except Exception:
    ts_str = datetime.datetime.now().strftime("%H%M%S")
    proc_excel_path = os.path.join(carpeta_proc, f"Reporte_Asistencia_GZG_{fecha_inicio}_al_{fecha_hoy}_{ts_str}.xlsx")
    with open(proc_excel_path, "wb") as f:
        f.write(excel_bytes)

conn.close()

print(f"=== PROCESAMIENTO COMPLETADO ===")
print(f"Marcaciones crudas: {len(df_marc)}")
print(f"Filas de asistencia procesadas: {len(df_asist)}")
print(f"Reporte procesado guardado en: {proc_excel_path}")
