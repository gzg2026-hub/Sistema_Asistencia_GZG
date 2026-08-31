import pandas as pd
import sqlite3
import os

db_path = 'data/asistencia.db'
padron_path = 'Padron_Trabajadores_GZG.xlsx'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Leer y sincronizar Padron_Trabajadores_GZG.xlsx en la tabla trabajadores
if os.path.exists(padron_path):
    df_test = pd.read_excel(padron_path, header=None)
    header_idx = 0
    for i in range(min(10, len(df_test))):
        vals = [str(v).upper() for v in df_test.iloc[i].values]
        if any('DNI' in v for v in vals) or any('APELLIDOS' in v for v in vals):
            header_idx = i
            break
    
    df_padron = pd.read_excel(padron_path, header=header_idx)
    
    col_map = {}
    for c in df_padron.columns:
        c_str = str(c).upper()
        if 'DNI' in c_str:
            col_map[c] = 'dni'
        elif 'APELLIDO' in c_str:
            col_map[c] = 'apellidos'
        elif 'NOMBRE' in c_str:
            col_map[c] = 'nombres'
        elif 'DEPARTAMENTO' in c_str or 'ÁREA' in c_str or 'AREA' in c_str:
            col_map[c] = 'area'
        elif 'POSICIÓN' in c_str or 'POSICION' in c_str or 'CARGO' in c_str:
            col_map[c] = 'cargo'
        elif 'NIVEL DE APROBACION 1' in c_str or 'APROBADOR 1' in c_str or 'APROBACION 1' in c_str:
            col_map[c] = 'aprobador_n1'
        elif 'NIVEL DE APROBACION 2' in c_str or 'APROBADOR 2' in c_str or 'APROBACION 2' in c_str:
            col_map[c] = 'aprobador_n2'
            
    df_padron = df_padron.rename(columns=col_map)
    
    for _, row in df_padron.iterrows():
        raw_dni = str(row.get('dni', '')).replace('.0', '').strip()
        digits = ''.join(filter(str.isdigit, raw_dni))
        if not digits:
            continue
        dni = digits.lstrip('0').zfill(8)
        apellidos = str(row.get('apellidos', '')).strip()
        nombres = str(row.get('nombres', '')).strip()
        cargo = str(row.get('cargo', '')).strip()
        area = str(row.get('area', '')).strip()
        app_n1 = str(row.get('aprobador_n1', '')).strip() if pd.notna(row.get('aprobador_n1')) else None
        app_n2 = str(row.get('aprobador_n2', '')).strip() if pd.notna(row.get('aprobador_n2')) else None
        
        cursor.execute("""
        INSERT INTO trabajadores (dni, apellidos, nombres, cargo, area, aprobador_n1, aprobador_n2, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(dni) DO UPDATE SET
            apellidos=excluded.apellidos,
            nombres=excluded.nombres,
            cargo=excluded.cargo,
            area=excluded.area,
            aprobador_n1=excluded.aprobador_n1,
            aprobador_n2=excluded.aprobador_n2,
            updated_at=CURRENT_TIMESTAMP
        """, (dni, apellidos, nombres, cargo, area, app_n1, app_n2))

# 2. Actualizar el usuario jdelariva en la tabla usuarios
cursor.execute("""
UPDATE usuarios 
SET rol = 'JEFE',
    cargo = 'Jefe',
    area_asignada = 'Jefatura'
WHERE username = 'jdelariva'
""")

# 3. Actualizar cargos en asistencia y aprobaciones para Javier de la Riva
cursor.execute("""
UPDATE asistencia
SET cargo = 'Jefe',
    area = 'Jefatura'
WHERE dni = '72559194'
""")

cursor.execute("""
UPDATE aprobaciones
SET cargo = 'Jefe',
    area = 'Jefatura'
WHERE dni = '72559194'
""")

conn.commit()

# 4. Verificar resultados
cursor.execute("SELECT dni, apellidos, nombres, cargo, area, aprobador_n1, aprobador_n2 FROM trabajadores WHERE dni = '72559194'")
trab = cursor.fetchone()
print("\n[OK] Trabajador actualizado en SQLite:")
print("    DNI:", trab[0])
print("    Nombre:", trab[2], trab[1])
print("    Cargo:", trab[3])
print("    Área:", trab[4])
print("    Aprobador N1:", trab[5])
print("    Aprobador N2:", trab[6])

cursor.execute("SELECT username, nombre_completo, rol, cargo, area_asignada FROM usuarios WHERE username = 'jdelariva'")
usr = cursor.fetchone()
print("\n[OK] Usuario RBAC actualizado en SQLite:")
print("    Username:", usr[0])
print("    Nombre:", usr[1])
print("    Rol:", usr[2])
print("    Cargo:", usr[3])
print("    Área:", usr[4])

conn.close()
