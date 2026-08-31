import os
import shutil
import sqlite3

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
db_path = os.path.join(PROJECT_ROOT, "data", "asistencia.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables_to_reindex = ['marcaciones_raw', 'asistencia', 'horas_extra', 'incidencias']

print("=== REINDEXANDO IDs DE 1 A N Y REINICIANDO SQLITE SEQUENCE ===")

for table in tables_to_reindex:
    # 1. Obtener información de columnas excluyendo 'id'
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cursor.fetchall() if c[1] != 'id']
    cols_str = ", ".join(cols)
    
    # 2. Copiar contenido ordenado a tabla temporal
    cursor.execute(f"CREATE TABLE {table}_temp AS SELECT {cols_str} FROM {table};")
    
    # 3. Vaciar la tabla original
    cursor.execute(f"DELETE FROM {table};")
    
    # 4. Eliminar entrada en sqlite_sequence para la tabla
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,))
    
    # 5. Reinsertar los datos para que el autoincremento empiece estrictamente en 1
    cursor.execute(f"INSERT INTO {table} ({cols_str}) SELECT {cols_str} FROM {table}_temp;")
    
    # 6. Eliminar tabla temporal
    cursor.execute(f"DROP TABLE {table}_temp;")
    
    cursor.execute(f"SELECT MIN(id), MAX(id), COUNT(*) FROM {table}")
    min_id, max_id, count = cursor.fetchone()
    print(f"[OK] Tabla '{table}': {count} filas | IDs reordenados del {min_id} al {max_id}")

conn.commit()
cursor.execute("VACUUM;")
conn.close()

print("\n[OK] Reindexacion completada exitosamente. Todos los IDs ahora empiezan en 1!")
