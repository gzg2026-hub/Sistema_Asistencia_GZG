import os
import sys
import sqlite3
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import get_connection, DB_PATH, obtener_trabajadores_master, obtener_datos_db, guardar_asistencia_y_reportes
from core.attendance_engine import procesar_asistencia_df

print("=== POBLANDO INCIDENCIAS OFICIALES EN SQLITE ===")

# 1. Obtener marcaciones y calcular incidencias oficiales
df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

df_asis, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

print(f"Marcaciones evaluadas: {len(df_marc)}")
print(f"Incidencias oficiales generadas por el motor: {len(df_inc)}")

# 2. Guardar asistencia e incidencias en SQLite
guardar_asistencia_y_reportes(df_asis, df_he, df_inc)

conn = get_connection(DB_PATH)
cursor = conn.cursor()

cursor.execute("DELETE FROM incidencias;")
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'incidencias';")

if not df_inc.empty:
    for _, r in df_inc.iterrows():
        cursor.execute("""
            INSERT INTO incidencias (
                fecha, dni, apellidos, nombres, cargo, area, tipo, hora, descripcion, severidad, observacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(r.get('FECHA', '')),
            str(r.get('DNI', '')),
            str(r.get('APELLIDOS', '')),
            str(r.get('NOMBRES', '')),
            str(r.get('CARGO', '')),
            str(r.get('ÁREA', r.get('AREA', ''))),
            str(r.get('TIPO', '')),
            str(r.get('HORA', '')),
            str(r.get('DESCRIPCIÓN', r.get('DESCRIPCION', ''))),
            str(r.get('SEVERIDAD', '')),
            str(r.get('OBSERVACIÓN', r.get('OBSERVACION', '')))
        ))

conn.commit()

# Reindexar IDs del 1 al N para incidencias
cursor.execute("PRAGMA table_info(incidencias)")
cols = [c[1] for c in cursor.fetchall() if c[1] != 'id']
cols_str = ", ".join(cols)

cursor.execute("CREATE TABLE incidencias_temp AS SELECT * FROM incidencias;")
cursor.execute("DELETE FROM incidencias;")
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'incidencias';")

# Reinsertar columnas que coincidan
cursor.execute(f"INSERT INTO incidencias ({cols_str}) SELECT {cols_str} FROM incidencias_temp;")
cursor.execute("DROP TABLE incidencias_temp;")

conn.commit()

cursor.execute("SELECT COUNT(*), MIN(id), MAX(id) FROM incidencias")
count, min_id, max_id = cursor.fetchone()
print(f"[OK] Tabla 'incidencias' guardada exitosamente: {count} filas | IDs del {min_id} al {max_id}")

conn.close()
