import sqlite3, pandas as pd

conn = sqlite3.connect(r'c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\data\asistencia.db')

print('=== APROBACIONES PARA SILVA ===')
df_aprob = pd.read_sql_query("SELECT id, dni, apellidos, nombres, fecha, entrada, salida, horas_extras_hhmm, exceso_jornada_hhmm FROM aprobaciones WHERE apellidos LIKE '%SILVA%'", conn)
print(df_aprob.to_string())

print('\n=== ASISTENCIA PARA SILVA EL 2026-08-24 ===')
df_asist = pd.read_sql_query("SELECT * FROM asistencia WHERE apellidos LIKE '%SILVA%'", conn)
print(df_asist[['dni', 'apellidos', 'nombres', 'fecha', 'entrada', 'salida', 'horas_trabajadas']].to_string())

conn.close()
