import sqlite3
import pandas as pd
import os
from typing import Tuple, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "asistencia.db")

def get_connection(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    return conn

def init_db(db_path: str = DB_PATH):
    """Inicializa la base de datos con las tablas estructuradas si no existen."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # 1. Tabla TRABAJADORES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trabajadores (
        dni TEXT PRIMARY KEY,
        apellidos TEXT,
        nombres TEXT,
        cargo TEXT,
        area TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Tabla MARCACIONES_RAW
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marcaciones_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT,
        nombre TEXT,
        apellido TEXT,
        cargo TEXT,
        departamento TEXT,
        grupo TEXT,
        fecha TEXT,
        semana TEXT,
        tiempo TEXT,
        tipo_pase TEXT,
        metodo_verificacion TEXT,
        punto_control TEXT,
        archivo_origen TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(dni, fecha, tiempo, tipo_pase) ON CONFLICT REPLACE
    )
    """)
    
    # 3. Tabla ASISTENCIA (Hoja 03_ASISTENCIA)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        dni TEXT,
        apellidos TEXT,
        nombres TEXT,
        cargo TEXT,
        area TEXT,
        turno TEXT,
        entrada TEXT,
        salida TEXT,
        horas_trabajadas REAL,
        tardanza_min INTEGER,
        salida_anticipada_min INTEGER,
        exceso_jornada_min INTEGER,
        total_horas_adicionales_min INTEGER,
        incidencias TEXT,
        estado_asistencia TEXT,
        observaciones TEXT,
        UNIQUE(fecha, dni) ON CONFLICT REPLACE
    )
    """)
    
    # 4. Tabla HORAS_EXTRA (Hoja 04_HORAS_EXTRA)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS horas_extra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        dni TEXT,
        apellidos TEXT,
        nombres TEXT,
        cargo TEXT,
        area TEXT,
        turno TEXT,
        inicio_he TEXT,
        fin_he TEXT,
        duracion_min INTEGER,
        observacion TEXT,
        UNIQUE(fecha, dni, inicio_he, fin_he) ON CONFLICT REPLACE
    )
    """)
    
    # 5. Tabla INCIDENCIAS (Hoja 05_INCIDENCIAS)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        dni TEXT,
        apellidos TEXT,
        nombres TEXT,
        cargo TEXT,
        area TEXT,
        tipo TEXT,
        hora TEXT,
        descripcion TEXT,
        severidad TEXT,
        observacion TEXT
    )
    """)

    # 6. Tabla USUARIOS para RBAC y Autenticación
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre_completo TEXT NOT NULL,
        rol TEXT NOT NULL,
        area_asignada TEXT DEFAULT 'TODAS',
        cargo TEXT DEFAULT '',
        activo INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Migración segura de columnas de validación en horas_extra e incidencias
    cols_he = [row[1] for row in cursor.execute("PRAGMA table_info(horas_extra)").fetchall()]
    if 'estado_validacion' not in cols_he:
        cursor.execute("ALTER TABLE horas_extra ADD COLUMN estado_validacion TEXT DEFAULT 'PENDIENTE'")
        cursor.execute("ALTER TABLE horas_extra ADD COLUMN validado_por TEXT")
        cursor.execute("ALTER TABLE horas_extra ADD COLUMN fecha_validacion TEXT")
        cursor.execute("ALTER TABLE horas_extra ADD COLUMN observacion_validacion TEXT")

    cols_inc = [row[1] for row in cursor.execute("PRAGMA table_info(incidencias)").fetchall()]
    if 'estado_validacion' not in cols_inc:
        cursor.execute("ALTER TABLE incidencias ADD COLUMN estado_validacion TEXT DEFAULT 'PENDIENTE'")
        cursor.execute("ALTER TABLE incidencias ADD COLUMN validado_por TEXT")
        cursor.execute("ALTER TABLE incidencias ADD COLUMN fecha_validacion TEXT")
        cursor.execute("ALTER TABLE incidencias ADD COLUMN observacion_validacion TEXT")

    conn.commit()
    conn.close()

def guardar_trabajadores(df_trabajadores: pd.DataFrame, db_path: str = DB_PATH):
    """Guarda o actualiza la lista de trabajadores maestros."""
    if df_trabajadores.empty:
        return
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    for _, row in df_trabajadores.iterrows():
        dni = str(row.get('DNI', '')).strip()
        if not dni or dni == 'nan':
            continue
        cursor.execute("""
        INSERT INTO trabajadores (dni, apellidos, nombres, cargo, area, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(dni) DO UPDATE SET
            apellidos=excluded.apellidos,
            nombres=excluded.nombres,
            cargo=excluded.cargo,
            area=excluded.area,
            updated_at=CURRENT_TIMESTAMP
        """, (
            dni,
            str(row.get('APELLIDOS', '')).strip(),
            str(row.get('NOMBRES', '')).strip(),
            str(row.get('CARGO', '')).strip(),
            str(row.get('AREA', row.get('ÁREA', ''))).strip()
        ))
    conn.commit()
    conn.close()

def guardar_marcaciones_raw(df_marcaciones: pd.DataFrame, archivo_origen: str = "", db_path: str = DB_PATH):
    """Inserta transacciones de marcación raw en la base de datos."""
    if df_marcaciones.empty:
        return
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Obtener mapa DNI -> CARGO de la tabla trabajadores si existe
    cargo_map = {}
    try:
        df_trab_map = pd.read_sql_query("SELECT dni, cargo FROM trabajadores", conn)
        for _, tr in df_trab_map.iterrows():
            cargo_map[str(tr['dni']).strip()] = str(tr['cargo']).strip()
    except Exception:
        pass
        
    for _, row in df_marcaciones.iterrows():
        dni = str(row.get('ID', row.get('DNI', ''))).strip()
        fecha = str(row.get('Fecha', '')).strip()
        tiempo = str(row.get('Tiempo', '')).strip()
        tipo_pase = str(row.get('Tipo de pase de tarjeta', '')).strip()
        
        if not dni or not fecha:
            continue
            
        # Limpieza de departamento (extraer texto tras el >)
        dept_val = str(row.get('Departamento', '')).strip()
        if '>' in dept_val:
            dept_val = dept_val.split('>')[-1].strip()
            
        # Obtener cargo del row o del mapa de trabajadores por DNI
        cargo_val = str(row.get('Cargo', row.get('CARGO', ''))).strip()
        if not cargo_val and dni in cargo_map:
            cargo_val = cargo_map[dni]
            
        cursor.execute("""
        INSERT INTO marcaciones_raw (
            dni, nombre, apellido, cargo, departamento, grupo, fecha, semana, tiempo,
            tipo_pase, metodo_verificacion, punto_control, archivo_origen
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(dni, fecha, tiempo, tipo_pase) DO NOTHING
        """, (
            dni,
            str(row.get('Nombre', '')),
            str(row.get('Apellido', '')),
            cargo_val,
            dept_val,
            str(row.get('Grupo de asistencia', '')),
            fecha,
            str(row.get('Semana', '')),
            tiempo,
            tipo_pase,
            str(row.get('Método de verificación', '')),
            str(row.get('Punto de control de asistencia', '')),
            archivo_origen
        ))
    conn.commit()
    conn.close()

def guardar_asistencia_y_reportes(df_asistencia: pd.DataFrame, df_horas_extra: pd.DataFrame, df_incidencias: pd.DataFrame, db_path: str = DB_PATH):
    """Guarda los resultados procesados de asistencia, H.E. e incidencias."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # 1. Asistencia
    if not df_asistencia.empty:
        for _, r in df_asistencia.iterrows():
            cursor.execute("""
            INSERT INTO asistencia (
                fecha, dni, apellidos, nombres, cargo, area, turno,
                entrada, salida, horas_trabajadas, tardanza_min, salida_anticipada_min,
                exceso_jornada_min, total_horas_adicionales_min, incidencias, estado_asistencia, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(fecha, dni) DO UPDATE SET
                apellidos=excluded.apellidos,
                nombres=excluded.nombres,
                cargo=excluded.cargo,
                area=excluded.area,
                turno=excluded.turno,
                entrada=excluded.entrada,
                salida=excluded.salida,
                horas_trabajadas=excluded.horas_trabajadas,
                tardanza_min=excluded.tardanza_min,
                salida_anticipada_min=excluded.salida_anticipada_min,
                exceso_jornada_min=excluded.exceso_jornada_min,
                total_horas_adicionales_min=excluded.total_horas_adicionales_min,
                incidencias=excluded.incidencias,
                estado_asistencia=excluded.estado_asistencia,
                observaciones=excluded.observaciones
            """, (
                str(r.get('FECHA', '')),
                str(r.get('DNI', '')),
                str(r.get('APELLIDOS', '')),
                str(r.get('NOMBRES', '')),
                str(r.get('CARGO', '')),
                str(r.get('ÁREA', r.get('AREA', ''))),
                str(r.get('TURNO', '')),
                r.get('ENTRADA', None),
                r.get('SALIDA', None),
                float(r.get('HORAS TRABAJADAS', r.get('HORAS_TRABAJADAS', 0.0)) or 0.0),
                int(r.get('TARDANZA (MIN)', r.get('TARDANZA_MIN', 0)) or 0),
                int(r.get('SALIDA ANTICIPADA (MIN)', r.get('SALIDA_ANTICIPADA_MIN', 0)) or 0),
                int(r.get('EXCESO JORNADA', r.get('EXCESO_JORNADA_MIN', 0)) or 0),
                int(r.get('TOTAL HORAS ADICIONALES', r.get('TOTAL_HORAS_ADICIONALES_MIN', 0)) or 0),
                str(r.get('INCIDENCIAS', '')),
                str(r.get('ESTADO ASISTENCIA', r.get('ESTADO', ''))),
                str(r.get('OBSERVACIONES', ''))
            ))
            
    # 2. Horas Extra
    if not df_horas_extra.empty:
        for _, r in df_horas_extra.iterrows():
            cursor.execute("""
            INSERT INTO horas_extra (
                fecha, dni, apellidos, nombres, cargo, area, turno, inicio_he, fin_he, duracion_min, observacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(fecha, dni, inicio_he, fin_he) DO UPDATE SET
                cargo=excluded.cargo,
                area=excluded.area,
                duracion_min=excluded.duracion_min,
                observacion=excluded.observacion
            """, (
                str(r.get('FECHA', '')),
                str(r.get('DNI', '')),
                str(r.get('APELLIDOS', '')),
                str(r.get('NOMBRES', '')),
                str(r.get('CARGO', '')),
                str(r.get('ÁREA', r.get('AREA', ''))),
                str(r.get('TURNO', '')),
                str(r.get('INICIO H.E.', r.get('INICIO_HE', ''))),
                str(r.get('FIN H.E.', r.get('FIN_HE', ''))),
                int(r.get('DURACIÓN', r.get('DURACION_MIN', 0)) or 0),
                str(r.get('OBSERVACIÓN', r.get('OBSERVACION', '')))
            ))

    # 3. Incidencias
    if not df_incidencias.empty:
        for _, r in df_incidencias.iterrows():
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
    conn.close()

def format_hhmm_cell(val, is_hours_float=False) -> str:
    """Convierte minutos enteros u horas flotantes a string HH:MM (ej. 11:51, 00:15)."""
    if pd.isna(val) or val is None or val == "":
        return "00:00"
    val_str = str(val).strip()
    if ":" in val_str and len(val_str.split(":")) == 2:
        parts = val_str.split(":")
        try:
            h = int(parts[0])
            m = int(parts[1])
            return f"{h:02d}:{m:02d}"
        except Exception:
            return val_str
    try:
        num = float(val)
        if num <= 0:
            return "00:00"
        total_min = int(round(num * 60.0)) if is_hours_float else int(round(num))
        h = total_min // 60
        m = total_min % 60
        return f"{h:02d}:{m:02d}"
    except Exception:
        return "00:00"

def obtener_datos_db(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None, db_path: str = DB_PATH) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Obtiene DataFrames acumulados desde la base de datos:
    (df_trabajadores, df_marcaciones, df_asistencia, df_horas_extra, df_incidencias)
    """
    init_db(db_path)
    conn = get_connection(db_path)
    
    # 1. Trabajadores
    df_trabajadores = pd.read_sql_query("SELECT dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES, cargo as CARGO, area as AREA FROM trabajadores ORDER BY apellidos, nombres", conn)
    
    where_clause = ""
    params = []
    if fecha_inicio and fecha_fin:
        where_clause = " WHERE fecha >= ? AND fecha <= ? "
        params = [fecha_inicio, fecha_fin]
    elif fecha_inicio:
        where_clause = " WHERE fecha >= ? "
        params = [fecha_inicio]
    elif fecha_fin:
        where_clause = " WHERE fecha <= ? "
        params = [fecha_fin]

    # 2. Marcaciones Raw (Orden oficial estricto: ID, Fecha, Nombre, Apellido, Cargo, Departamento...)
    query_mar = f"""
    SELECT m.dni as ID, m.fecha as Fecha, m.nombre as Nombre, m.apellido as Apellido,
           COALESCE(NULLIF(m.cargo, ''), t.cargo, '') as Cargo,
           m.departamento as Departamento, m.grupo as 'Grupo de asistencia',
           m.tiempo as Tiempo, m.tipo_pase as 'Tipo de pase de tarjeta',
           m.metodo_verificacion as 'Método de verificación',
           m.punto_control as 'Punto de control de asistencia'
    FROM marcaciones_raw m
    LEFT JOIN trabajadores t ON m.dni = t.dni
    {where_clause.replace('fecha', 'm.fecha') if where_clause else ''}
    ORDER BY m.fecha, m.tiempo
    """
    df_marcaciones = pd.read_sql_query(query_mar, conn, params=params)
    
    # 3. Asistencia
    query_asis = f"""
    SELECT fecha as FECHA, dni as DNI, apellidos as APELLIDOS, nombres as NOMBRES,
           cargo as CARGO, area as ÁREA, turno as TURNO,
           entrada as ENTRADA, salida as SALIDA,
           horas_trabajadas as 'HORAS TRABAJADAS',
           tardanza_min as 'TARDANZA (MIN)',
           salida_anticipada_min as 'SALIDA ANTICIPADA (MIN)',
           exceso_jornada_min as 'EXCESO JORNADA',
           total_horas_adicionales_min as 'TOTAL HORAS ADICIONALES',
           incidencias as INCIDENCIAS, estado_asistencia as 'ESTADO ASISTENCIA', observaciones as OBSERVACIONES
    FROM asistencia {where_clause} ORDER BY fecha, apellidos, nombres
    """
    df_asistencia = pd.read_sql_query(query_asis, conn, params=params)

    if not df_asistencia.empty:
        df_asistencia['HORAS TRABAJADAS (HH:MM)'] = df_asistencia['HORAS TRABAJADAS'].apply(lambda x: format_hhmm_cell(x, is_hours_float=True))
        df_asistencia['TARDANZA (HH:MM)'] = df_asistencia['TARDANZA (MIN)'].apply(lambda x: format_hhmm_cell(x, is_hours_float=False))
        df_asistencia['SALIDA ANTICIPADA (HH:MM)'] = df_asistencia['SALIDA ANTICIPADA (MIN)'].apply(lambda x: format_hhmm_cell(x, is_hours_float=False))
        df_asistencia['EXCESO JORNADA (HH:MM)'] = df_asistencia['EXCESO JORNADA'].apply(lambda x: format_hhmm_cell(x, is_hours_float=False))
        df_asistencia['TOTAL HORAS ADICIONALES (HH:MM)'] = df_asistencia['TOTAL HORAS ADICIONALES'].apply(lambda x: format_hhmm_cell(x, is_hours_float=False))
    
    # 4. Horas Extra
    query_he = f"""
    SELECT h.id as ID_REGISTRO, h.fecha as FECHA, h.dni as DNI, h.apellidos as APELLIDOS, h.nombres as NOMBRES,
           COALESCE(NULLIF(h.cargo, ''), t.cargo, '') as CARGO,
           COALESCE(NULLIF(h.area, ''), t.area, '') as ÁREA,
           h.turno as TURNO, h.inicio_he as 'INICIO H.E.', h.fin_he as 'FIN H.E.',
           h.duracion_min as 'DURACIÓN',
           h.observacion as OBSERVACIÓN,
           COALESCE(h.estado_validacion, 'PENDIENTE') as 'ESTADO VALIDADOR',
           COALESCE(h.validado_por, '-') as 'VALIDADO POR',
           COALESCE(h.fecha_validacion, '-') as 'FECHA VALIDACIÓN',
           COALESCE(h.observacion_validacion, '') as 'OBSERVACIÓN VALIDADOR'
    FROM horas_extra h
    LEFT JOIN trabajadores t ON h.dni = t.dni
    {where_clause.replace('fecha', 'h.fecha') if where_clause else ''}
    ORDER BY h.fecha, h.apellidos, h.nombres
    """
    df_horas_extra = pd.read_sql_query(query_he, conn, params=params)

    if not df_horas_extra.empty:
        df_horas_extra['DURACIÓN (HH:MM)'] = df_horas_extra['DURACIÓN'].apply(lambda x: format_hhmm_cell(x, is_hours_float=False))
    
    # 5. Incidencias
    query_inc = f"""
    SELECT i.id as ID_REGISTRO, i.fecha as FECHA, i.dni as DNI, i.apellidos as APELLIDOS, i.nombres as NOMBRES,
           COALESCE(NULLIF(i.cargo, ''), t.cargo, '') as CARGO,
           COALESCE(NULLIF(i.area, ''), t.area, '') as ÁREA,
           i.tipo as TIPO, i.hora as HORA, i.descripcion as DESCRIPCIÓN,
           i.severidad as SEVERIDAD, i.observacion as OBSERVACIÓN,
           COALESCE(i.estado_validacion, 'PENDIENTE') as 'ESTADO VALIDADOR',
           COALESCE(i.validado_por, '-') as 'VALIDADO POR',
           COALESCE(i.fecha_validacion, '-') as 'FECHA VALIDACIÓN',
           COALESCE(i.observacion_validacion, '') as 'OBSERVACIÓN VALIDADOR'
    FROM incidencias i
    LEFT JOIN trabajadores t ON i.dni = t.dni
    {where_clause.replace('fecha', 'i.fecha') if where_clause else ''}
    ORDER BY i.fecha, i.apellidos, i.nombres
    """
    df_incidencias = pd.read_sql_query(query_inc, conn, params=params)
    
    conn.close()
    return df_trabajadores, df_marcaciones, df_asistencia, df_horas_extra, df_incidencias

# ==============================================================================
# FUNCIONES DE GESTIÓN DE USUARIOS Y AUTENTICACIÓN (RBAC)
# ==============================================================================

def seed_default_users(hash_fn, db_path: str = DB_PATH):
    """Crea los usuarios iniciales del sistema si no existen."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    users = [
        ('admin', hash_fn('gzg2026*'), 'Administración RRHH', 'ADMINISTRACION', 'TODAS', 'Administrador de Sistema'),
        ('raul.espinoza', hash_fn('gzg2026*'), 'Ing. Raúl Espinoza', 'GERENTE_GENERAL', 'TODAS', 'Gerente General'),
        ('jhon.alva', hash_fn('gzg2026*'), 'Ing. Jhon Alva', 'GERENTE_PLANTA', 'TODAS', 'Gerente de Planta'),
        ('carlos.mendoza', hash_fn('gzg2026*'), 'Ing. Carlos Mendoza', 'SUPERINTENDENTE', 'TODAS', 'Superintendente de Mina'),
        ('manuel.benitez', hash_fn('gzg2026*'), 'Ing. Manuel Benítez', 'JEFE_SUPERVISOR', 'OPER&MTTO', 'Jefe de Operaciones'),
        ('javier.delariva', hash_fn('gzg2026*'), 'Lic. Javier De La Riva', 'JEFE_SUPERVISOR', 'JEFATURA', 'Supervisor de Jefatura')
    ]
    
    for username, pass_hash, nombre, rol, area, cargo in users:
        cursor.execute("""
        INSERT OR REPLACE INTO usuarios (username, password_hash, nombre_completo, rol, area_asignada, cargo)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (username, pass_hash, nombre, rol, area, cargo))
        
    conn.commit()
    conn.close()

def obtener_usuario_by_username(username: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Obtiene la información de un usuario según su nombre de usuario (búsqueda case-insensitive)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, nombre_completo, rol, area_asignada, cargo, activo FROM usuarios WHERE LOWER(username) = LOWER(?)", (username.strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'password_hash': row[2],
            'nombre_completo': row[3],
            'rol': row[4],
            'area_asignada': row[5],
            'cargo': row[6],
            'activo': row[7]
        }
    return None

def obtener_todos_usuarios(db_path: str = DB_PATH) -> pd.DataFrame:
    """Retorna la lista de todos los usuarios registrados."""
    conn = get_connection(db_path)
    df = pd.read_sql_query("SELECT id, username, nombre_completo, rol, area_asignada, cargo, activo, created_at FROM usuarios ORDER BY nombre_completo", conn)
    conn.close()
    return df

def crear_usuario(username: str, password_hash: str, nombre_completo: str, rol: str, area_asignada: str = 'TODAS', cargo: str = '', db_path: str = DB_PATH) -> bool:
    """Crea un nuevo usuario en la base de datos."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO usuarios (username, password_hash, nombre_completo, rol, area_asignada, cargo)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (username.strip(), password_hash, nombre_completo.strip(), rol, area_asignada, cargo.strip()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        conn.close()
        return False

def eliminar_usuario(user_id: int, db_path: str = DB_PATH) -> bool:
    """Desactiva o elimina un usuario."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def actualizar_estado_he(he_id: int, nuevo_estado: str, usuario_validador: str, observacion: str = "", db_path: str = DB_PATH) -> bool:
    """Actualiza el estado de validación de un registro de Horas Extra."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    fecha_val = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    UPDATE horas_extra
    SET estado_validacion = ?, validado_por = ?, fecha_validacion = ?, observacion_validacion = ?
    WHERE id = ?
    """, (nuevo_estado, usuario_validador, fecha_val, observacion, he_id))
    conn.commit()
    conn.close()
    return True

def actualizar_estado_incidencia(inc_id: int, nuevo_estado: str, usuario_validador: str, observacion: str = "", db_path: str = DB_PATH) -> bool:
    """Actualiza el estado de validación de un registro de Incidencias."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    fecha_val = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    UPDATE incidencias
    SET estado_validacion = ?, validado_por = ?, fecha_validacion = ?, observacion_validacion = ?
    WHERE id = ?
    """, (nuevo_estado, usuario_validador, fecha_val, observacion, inc_id))
    conn.commit()
    conn.close()
    return True

