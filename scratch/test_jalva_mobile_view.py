import sqlite3, os
import pandas as pd

conn = sqlite3.connect('data/asistencia.db')

u_lower = 'jalva'
rol = 'JEFE'

# Query matching mobile.py logic
query = """
    SELECT id, fecha, dni, apellidos, nombres, cargo, area,
           entrada, salida, horas_trabajadas, jornada_trabajada_hhmm,
           horas_extras_min, exceso_jornada_min, horas_extras_hhmm,
           exceso_jornada_hhmm, observacion_trabajador,
           aprobador_n1, aprobador_n2, estado, estado_n1, estado_n2,
           comentario_supervisor, fecha_aprobacion
    FROM aprobaciones
    WHERE LOWER(TRIM(COALESCE(aprobador_n1, ''))) = ?
       OR LOWER(TRIM(COALESCE(aprobador_n2, ''))) = ?
    ORDER BY fecha DESC, id DESC
"""
df = pd.read_sql_query(query, conn, params=(u_lower, u_lower))
conn.close()

print(f"=== Bandeja jalva ({len(df)} total solicitudes) ===")
print(df[['id', 'fecha', 'apellidos', 'nombres', 'horas_extras_hhmm', 'exceso_jornada_hhmm', 'estado', 'estado_n1', 'aprobador_n1']].to_string())

# Filtrar pendientes para N1
df_pend_n1 = df[(df['aprobador_n1'].str.lower() == u_lower) & (df['estado_n1'] == 'PENDIENTE')]
print(f"\nPendientes N1 para jalva: {len(df_pend_n1)}")
for _, r in df_pend_n1.iterrows():
    print(f" - {r['fecha']} | {r['apellidos']} {r['nombres']} | HE: {r['horas_extras_hhmm']} | Exceso: {r['exceso_jornada_hhmm']}")
