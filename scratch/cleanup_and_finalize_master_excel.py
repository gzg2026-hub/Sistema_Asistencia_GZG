import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import obtener_trabajadores_master, obtener_datos_db
from data.exporter import exportar_asistencia_excel
from core.attendance_engine import procesar_asistencia_df

# 1. Eliminar duplicados temporales
temp_files = ["Reporte_Asistencia_Procesado.xlsx", "Reporte_Asistencia_Procesado_Nuevo.xlsx"]
for fname in temp_files:
    fpath = os.path.join(ROOT_DIR, fname)
    if os.path.exists(fpath):
        try:
            os.remove(fpath)
            print(f"[OK] Eliminado duplicado temporal: {fname}")
        except Exception as e:
            print(f"[WARN] No se pudo eliminar {fname}: {e}")

# 2. Generar el único Excel Oficial: Sistema_Asistencia_GZG_v1.0.xlsx
df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db("2026-08-17", "2026-08-18")

if not df_trab.empty and not df_marc.empty:
    df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)
    excel_bytes = exportar_asistencia_excel(df_trab, df_marc, df_asis, df_he_out, df_inc)

    out_path = os.path.join(ROOT_DIR, "Sistema_Asistencia_GZG_v1.0.xlsx")
    try:
        with open(out_path, "wb") as f:
            f.write(excel_bytes)
        print(f"[OK] Excel Oficial generado exitosamente en: {out_path}")
    except PermissionError:
        print(f"[ERR] El archivo 'Sistema_Asistencia_GZG_v1.0.xlsx' está abierto en Excel. Por favor cierra Excel y reintenta.")
