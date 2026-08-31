import sqlite3

conn = sqlite3.connect('data/asistencia.db')

print('=== TOTAL SOLICITUDES POR SUPERVISOR N1 ===')
for r in conn.execute("SELECT aprobador_n1, COUNT(*) FROM aprobaciones GROUP BY aprobador_n1 ORDER BY COUNT(*) DESC").fetchall():
    print(' ', r)

print('\n=== SOLICITUDES DE JALVA ===')
jalva_rows = conn.execute("SELECT fecha, dni, apellidos, estado, estado_n1, aprobador_n1 FROM aprobaciones WHERE aprobador_n1='jalva' ORDER BY fecha").fetchall()
for r in jalva_rows:
    print(' ', r)
print(f'Total jalva: {len(jalva_rows)}')

print('\n=== SOLICITUDES DEL 24-AGO (TOTAL 8) ===')
for r in conn.execute("SELECT fecha, dni, apellidos, horas_extras_hhmm, exceso_jornada_hhmm, aprobador_n1, aprobador_n2 FROM aprobaciones WHERE fecha='2026-08-24' ORDER BY apellidos").fetchall():
    print(' ', r)

print('\n=== ESTADOS DE APROBACION ===')
for r in conn.execute("SELECT estado, COUNT(*) FROM aprobaciones GROUP BY estado").fetchall():
    print(' ', r)

conn.close()
