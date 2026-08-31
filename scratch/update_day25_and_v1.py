import os, sys, datetime
import pandas as pd

ROOT_DIR = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, ROOT_DIR)

from data.database import sincronizar_padron_desde_excel, obtener_trabajadores_master, DB_PATH
from data.data_loader import cargar_datos_excel
from core.attendance_engine import procesar_asistencia_df
from data.exporter import exportar_asistencia_excel, guardar_excel_base

# 1. Sincronizar Padron hacia SQLite (Solo lectura del Excel)
sincronizar_padron_desde_excel(DB_PATH)
df_trab = obtener_trabajadores_master()
print(f"Trabajadores cargados: {len(df_trab)}")

# 2. Cargar Transacciones Acumuladas
raw_path = os.path.join(ROOT_DIR, 'downloads', 'data_cruda', 'Transacciones_Acumuladas.xlsx')
_, df_marc, df_he = cargar_datos_excel(raw_path)
print(f"Marcaciones cargadas: {len(df_marc)}")

# 3. Procesar asistencia con el motor actualizado
df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc, df_he)
print(f"Asistencias procesadas totales: {len(df_asis)}")

# 4. Actualizar Sistema_Asistencia_GZG_v1.0.xlsx en la raiz
guardar_excel_base(df_trab, df_marc, df_asis, df_he_out, df_inc)
print("[OK] Sistema_Asistencia_GZG_v1.0.xlsx actualizado en la raiz.")

# 5. Generar Reporte Diario del 25 de Agosto
df_asis_25 = df_asis[df_asis['FECHA'].astype(str) == '2026-08-25']
print(f"Registros dia 25: {len(df_asis_25)}")

excel_bytes_25 = exportar_asistencia_excel(df_trab, df_marc, df_asis_25, df_he_out, df_inc)
diario_path = os.path.join(ROOT_DIR, 'downloads', 'data_procesada', 'diario', 'Reporte_Asistencia_GZG_2026-08-25.xlsx')
with open(diario_path, 'wb') as f:
    f.write(excel_bytes_25)
print(f"[OK] Reporte_Asistencia_GZG_2026-08-25.xlsx generado en: {diario_path}")

# 6. Verificar filas de Raul Lazaro y Clari Tocto en el dia 25
check_df = df_asis_25[df_asis_25['DNI'].astype(str).str.zfill(8).isin(['18074244', '77134790'])]
for _, r in check_df.iterrows():
    ape = r.get('APELLIDOS', '')
    nom = r.get('NOMBRES', '')
    tur = r.get('TURNO', '')
    ent = r.get('HORA_ENTRADA', '')
    sal = r.get('HORA_SALIDA', '')
    est = r.get('ESTADO', '')
    hrs = r.get('HORAS_TRABAJADAS_STR', '')
    print(f"Trabajador: {ape} {nom} | Turno: {tur} | Entrada: {ent} | Salida: {sal} | Estado: {est} | Horas: {hrs}")
