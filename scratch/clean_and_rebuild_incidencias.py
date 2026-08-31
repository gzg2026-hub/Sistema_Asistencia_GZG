import os
import sys
import sqlite3

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import get_connection, DB_PATH, obtener_trabajadores_master, obtener_datos_db, guardar_asistencia_y_reportes
from core.attendance_engine import procesar_asistencia_df

print("=== OPCCIÓN A: REGENERACIÓN LIMPIA Y OFICIAL DE INCIDENCIAS ===")

# 1. Vaciar las tablas de resultados calculados para eliminar residuos de pruebas pasadas
conn = get_connection(DB_PATH)
cursor = conn.cursor()

cursor.execute("DELETE FROM incidencias;")
cursor.execute("DELETE FROM asistencia;")
cursor.execute("DELETE FROM horas_extra;")
cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('incidencias', 'asistencia', 'horas_extra');")
conn.commit()
conn.close()

print("[OK] Vaciadas las tablas de resultados antiguos de pruebas.")

# 2. Cargar data cruda oficial e información de trabajadores
df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

print(f"Personal activo: {len(df_trab)} trabajadores")
print(f"Marcaciones raw oficiales: {len(df_marc)} marcaciones")

# 3. Recalcular la asistencia e incidencias oficiales en tiempo real
df_asis, df_he, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)

print(f"Incidencias oficiales calculadas: {len(df_inc)} incidencias realistas")
print(f"Asistencias diarias calculadas: {len(df_asis)} registros")
print(f"Horas extras calculadas: {len(df_he)} registros")

# 4. Guardar los nuevos datos 100% limpios en SQLite
guardar_asistencia_y_reportes(df_asis, df_he, df_inc)

# 5. Reindexar IDs del 1 a N
conn = get_connection(DB_PATH)
cursor = conn.cursor()
tables_to_reindex = ['incidencias', 'asistencia', 'horas_extra', 'marcaciones_raw']

for table in tables_to_reindex:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cursor.fetchall() if c[1] != 'id']
    cols_str = ", ".join(cols)
    
    cursor.execute(f"CREATE TABLE {table}_temp AS SELECT {cols_str} FROM {table};")
    cursor.execute(f"DELETE FROM {table};")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,))
    cursor.execute(f"INSERT INTO {table} ({cols_str}) SELECT {cols_str} FROM {table}_temp;")
    cursor.execute(f"DROP TABLE {table}_temp;")
    
    cursor.execute(f"SELECT MIN(id), MAX(id), COUNT(*) FROM {table}")
    min_id, max_id, count = cursor.fetchone()
    print(f"[OK] Tabla '{table}': {count} filas | IDs del {min_id} al {max_id}")

conn.commit()
cursor.execute("VACUUM;")
conn.close()

print("\n¡Regeneración limpia completada exitosamente! Tu base de datos SQLite ahora tiene solo datos 100% oficiales.")
