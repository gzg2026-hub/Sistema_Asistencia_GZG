import sqlite3, os

fname = 'scratch/test_57c5410.db'
print('File size:', os.path.getsize(fname))

try:
    conn = sqlite3.connect(fname)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print('Tables:', [r[0] for r in rows])
    
    total = conn.execute("SELECT COUNT(*) FROM trabajadores").fetchone()[0]
    print(f'Trabajadores: {total}')
    
    aprobadores = conn.execute("SELECT dni, apellidos, aprobador_n1, aprobador_n2 FROM trabajadores WHERE aprobador_n1 IS NOT NULL ORDER BY aprobador_n1, apellidos").fetchall()
    print(f'Con aprobador N1: {len(aprobadores)}')
    for r in aprobadores:
        print(' ', r)
    conn.close()
except Exception as e:
    print('Error:', type(e).__name__, e)
