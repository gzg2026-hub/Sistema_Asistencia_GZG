import sqlite3
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

db_path = os.path.join(ROOT_DIR, "data", "asistencia.db")

print(f"Limpiando datos simulados previos al 17 de Agosto de 2026 en: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Eliminar marcaciones_raw anteriores al 2026-08-17
cur.execute("DELETE FROM marcaciones_raw WHERE fecha < '2026-08-17';")
deleted_marc = cur.rowcount

# 2. Eliminar registros de asistencia anteriores al 2026-08-17
cur.execute("DELETE FROM asistencia WHERE fecha < '2026-08-17';")
deleted_asis = cur.rowcount

# 3. Eliminar registros de horas_extra anteriores al 2026-08-17
cur.execute("DELETE FROM horas_extra WHERE fecha < '2026-08-17';")
deleted_he = cur.rowcount

# 4. Eliminar incidencias anteriores al 2026-08-17
cur.execute("DELETE FROM incidencias WHERE fecha < '2026-08-17';")
deleted_inc = cur.rowcount

conn.commit()
conn.close()

print(f"\n[OK] Limpieza completada con éxito:")
print(f"  - Marcaciones de prueba eliminadas : {deleted_marc}")
print(f"  - Asistencias simuladas eliminadas  : {deleted_asis}")
print(f"  - Horas extras simuladas eliminadas : {deleted_he}")
print(f"  - Incidencias simuladas eliminadas  : {deleted_inc}")

# 5. Re-procesar asistencia oficial desde las marcaciones reales (17/08 y 18/08)
try:
    from data.database import obtener_trabajadores_master, obtener_datos_db, guardar_asistencia_y_reportes
    from data.exporter import guardar_excel_base
    from core.attendance_engine import procesar_asistencia_df

    df_trab = obtener_trabajadores_master()
    _, df_marc, _, _, _ = obtener_datos_db("2026-08-17", "2026-08-18")

    print(f"\n[INFO] Re-procesando asistencia real:")
    print(f"  - Trabajadores oficiales en padrón : {len(df_trab)}")
    print(f"  - Marcaciones reales (17 y 18 Ago)  : {len(df_marc)}")

    if not df_trab.empty and not df_marc.empty:
        df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)
        guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)
        guardar_excel_base(df_trab, df_marc, df_asis, df_he_out, df_inc)
        print(f"  - Asistencia real procesada y guardada : {len(df_asis)} registros")

except Exception as e:
    import traceback
    print(f"[WARN] Error al re-procesar asistencia: {e}")
    print(traceback.format_exc())
