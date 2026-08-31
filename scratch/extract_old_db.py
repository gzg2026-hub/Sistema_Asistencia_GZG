import subprocess, sqlite3, os

result = subprocess.run(['git', 'cat-file', 'blob', '57c5410:data/asistencia.db'], capture_output=True)
if result.returncode == 0:
    fname = 'scratch/recovered_asistencia.db'
    with open(fname, 'wb') as f:
        f.write(result.stdout)
    print(f'Saved {len(result.stdout)} bytes to {fname}')
    try:
        conn = sqlite3.connect(fname)
        tablas = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print('Tables:', tablas)
        
        total = conn.execute("SELECT COUNT(*) FROM trabajadores").fetchone()[0]
        print(f'Trabajadores: {total}')
        
        aprobadores = conn.execute(
            "SELECT dni, apellidos, aprobador_n1, aprobador_n2 FROM trabajadores WHERE aprobador_n1 IS NOT NULL ORDER BY aprobador_n1, apellidos"
        ).fetchall()
        print(f'Con aprobador N1: {len(aprobadores)}')
        for r in aprobadores:
            print(' ', r)
        conn.close()
    except Exception as e:
        print('Error:', type(e).__name__, e)
else:
    print('git error:', result.stderr.decode())
