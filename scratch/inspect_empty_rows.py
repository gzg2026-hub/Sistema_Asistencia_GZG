import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from core.attendance_engine import procesar_asistencia_df

df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db("2026-08-17", "2026-08-18")

print(f"Total Marcaciones en DB (17 y 18 Ago): {len(df_marc)}")
print(df_marc.groupby('Fecha').size() if 'Fecha' in df_marc.columns else "Sin col Fecha")

if not df_trab.empty and not df_marc.empty:
    df_asis, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)
    print("\n--- RESUMEN ASISTENCIA POR ESTADO ---")
    print(df_asis.groupby(['FECHA', 'ESTADO ASISTENCIA']).size())
    
    print("\n--- EJEMPLOS DE TRABAJADORES QUE SÍ TIENEN ENTRADA/SALIDA ---")
    con_entr = df_asis[df_asis['ENTRADA'].notna()]
    print(con_entr[['FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'ENTRADA', 'SALIDA', 'ESTADO ASISTENCIA']].head(15))
