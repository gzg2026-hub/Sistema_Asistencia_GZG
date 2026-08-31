import sqlite3

conn = sqlite3.connect('data/asistencia.db')
c = conn.cursor()
c.execute("SELECT id, dni, fecha, observacion_trabajador, comentario_n1, comentario_supervisor, motivo FROM aprobaciones")
rows = c.fetchall()
print("Total rows in aprobaciones:", len(rows))
con_algo = [r for r in rows if any(x and str(x).strip() not in ('', 'none', 'nan') for x in (r[3], r[4], r[5], r[6]))]
print("Rows with any comment/obs/motivo:", len(con_algo))
for r in con_algo:
    print(r)

c.execute("SELECT COUNT(*) FROM asistencia WHERE observaciones != '' AND observaciones IS NOT NULL")
print("Rows in asistencia with observaciones:", c.fetchone()[0])
