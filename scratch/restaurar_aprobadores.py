"""
Restaurar los aprobadores N1 y N2 en la tabla trabajadores desde la DB histórica de git.
Luego regenear las aprobaciones y exportar el Excel actualizado.
"""
import sqlite3, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.database import get_connection, DB_PATH, regenerar_aprobaciones_excel
from scripts.gdrive_uploader import subir_archivo_a_gdrive

# Mapa de aprobadores recuperado del git (commit 57c5410)
APROBADORES = {
    '40829439': ('jagreda', 'msanchez'),
    '70480441': ('jagreda', 'msanchez'),
    '73700691': ('jagreda', 'msanchez'),
    '78378144': ('jagreda', 'msanchez'),
    '19571505': ('jagreda', 'msanchez'),
    '06616501': ('jagreda', 'msanchez'),
    '71715827': ('jagreda', 'msanchez'),
    '70639427': ('jagreda', 'msanchez'),
    '60512609': ('jagreda', 'msanchez'),
    '18861684': ('jagreda', 'msanchez'),
    '60876523': ('jalva', 'msanchez'),
    '42626422': ('jalva', 'msanchez'),
    '72441086': ('jalva', 'msanchez'),
    '72909375': ('jalva', 'msanchez'),
    '76681582': ('jalva', 'msanchez'),
    '75464754': ('jalva', 'msanchez'),
    '42300003': ('jalva', 'msanchez'),
    '75741769': ('jalva', 'msanchez'),
    '45119078': ('jalva', 'msanchez'),
    '48790853': ('jalva', 'msanchez'),
    '71710175': ('jalva', 'msanchez'),
    '71710169': ('jalva', 'msanchez'),
    '62772089': ('jalva', 'msanchez'),
    '18074244': ('jalva', 'msanchez'),
    '74070928': ('jalva', 'msanchez'),
    '19678776': ('jalva', 'msanchez'),
    '78197802': ('jalva', 'msanchez'),
    '47591578': ('jalva', 'msanchez'),
    '72940900': ('jalva', 'msanchez'),
    '72940901': ('jalva', 'msanchez'),
    '70088280': ('jalva', 'msanchez'),
    '77386038': ('jalva', 'msanchez'),
    '72500789': ('jalva', 'msanchez'),
    '75539351': ('jalva', 'msanchez'),
    '73485498': ('jalva', 'msanchez'),
    '47721216': ('jdelariva', 'msanchez'),
    '41090274': ('jdelariva', 'msanchez'),
    '44196392': ('jhuayama', 'msanchez'),
    '03208053': ('jhuayama', 'msanchez'),
    '71060137': ('jhuayama', 'msanchez'),
    '44375240': ('jhuayama', 'msanchez'),
    '41219221': ('jhuayama', 'msanchez'),
    '47783594': ('msanchez', None),
    '47034929': ('msanchez', None),
    '72559194': ('msanchez', None),
    '44955960': ('msanchez', None),
    '46671923': ('msanchez', None),
    '75227437': ('msanchez', None),
    '70782038': ('msanchez', None),
}

conn = get_connection(DB_PATH)
cursor = conn.cursor()

print("=== RESTAURANDO APROBADORES EN trabajadores ===")
updated_t = 0
for dni, (n1, n2) in APROBADORES.items():
    cursor.execute(
        "UPDATE trabajadores SET aprobador_n1=?, aprobador_n2=? WHERE dni=?",
        (n1, n2, dni)
    )
    if cursor.rowcount > 0:
        updated_t += 1
conn.commit()
print(f"  Actualizados {updated_t} trabajadores")

print("=== RESTAURANDO APROBADORES EN aprobaciones ===")
updated_a = 0
for dni, (n1, n2) in APROBADORES.items():
    cursor.execute(
        "UPDATE aprobaciones SET aprobador_n1=?, aprobador_n2=? WHERE dni=?",
        (n1, n2, dni)
    )
    if cursor.rowcount > 0:
        updated_a += cursor.rowcount
conn.commit()
print(f"  Actualizadas {updated_a} filas de aprobaciones")

# Verificar jalva
rows_jalva = cursor.execute(
    "SELECT dni, fecha, estado, aprobador_n1 FROM aprobaciones WHERE aprobador_n1='jalva' ORDER BY fecha"
).fetchall()
print(f"\n=== JALVA N1 DESPUES: {len(rows_jalva)} solicitudes ===")
for r in rows_jalva: print(' ', r)

conn.close()

print("\n=== REGENERANDO EXCEL ===")
ok = regenerar_aprobaciones_excel(DB_PATH)
print(f"  Excel regenerado: {ok}")

print("\n=== SUBIENDO A GOOGLE DRIVE ===")
import datetime
mes = datetime.date.today().strftime('%Y-%m')
local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'downloads', 'data_procesada', f'Aprobaciones_GZG_{mes}.xlsx')
if os.path.exists(local_path):
    result = subir_archivo_a_gdrive(local_path)
    print(f"  Subido: {result}")
else:
    print(f"  ERROR: No existe {local_path}")

print("\nDONE")
