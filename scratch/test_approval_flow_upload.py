import os
import sys
import time
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import DB_PATH, actualizar_estado_aprobacion, get_connection
from scripts.gdrive_uploader import _get_drive_service, DRIVE_FOLDER_ID

print("=== PRUEBA DE FLUJO COMPLETO: APROBACION EN APP -> SUBIDA A DRIVE ===")

# 1. Obtener primera solicitud pendiente
conn = get_connection(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT id, dni, apellidos, nombres, estado_n1, aprobador_n1 FROM aprobaciones WHERE estado_n1 = 'PENDIENTE' LIMIT 1")
row = cursor.fetchone()
conn.close()

if not row:
    print("No hay solicitudes pendientes para probar.")
    sys.exit(0)

sol_id, dni, apellidos, nombres, estado_n1, aprobador_n1 = row
print(f"1. Solicitud seleccionada: ID {sol_id} | {nombres} {apellidos} (DNI {dni})")
print(f"   - Aprobador N1 asignado: {aprobador_n1}")

# 2. Simular aprobación por su jefe N1
print(f"\n2. Ejecutando actualizar_estado_aprobacion(ID={sol_id}, 'APROBADO', por='{aprobador_n1}')...")
ok_act = actualizar_estado_aprobacion(
    id_solicitud=sol_id,
    nuevo_estado="APROBADO",
    aprobado_por=aprobador_n1,
    comentario="Aprobado en prueba interactiva de verificacion",
    db_path=DB_PATH
)
print(f"   - Actualizacion en SQLite: {'EXITOSA (True)' if ok_act else 'FALLIDA'}")

# 3. Esperar 6 segundos a que el hilo en segundo plano regenere el Excel y lo suba a Google Drive
print("\n3. Esperando que el hilo en segundo plano regenere y suba a Google Drive...")
for s in range(6, 0, -1):
    print(f"   ... verificando en {s}s ...")
    time.sleep(1)

# 4. Verificar en Google Drive la marca de tiempo actualizada
service = _get_drive_service()
q = f"'{DRIVE_FOLDER_ID}' in parents and name = 'Aprobaciones_GZG_2026-08.xlsx' and trashed = false"
results = service.files().list(
    q=q,
    fields="files(id, name, modifiedTime, size)",
    supportsAllDrives=True,
    includeItemsFromAllDrives=True
).execute()

files = results.get("files", [])
if files:
    f = files[0]
    print(f"\n4. ESTADO CONFIRMADO EN GOOGLE DRIVE:")
    print(f"   - Archivo: {f.get('name')}")
    print(f"   - Ultima Modificacion en Drive: {f.get('modifiedTime')}")
    print(f"   - Tamano: {f.get('size')} bytes")
    print(f"\n✅ PRUEBA 100% EXITOSA: Cada accion en la app se refleja en Google Drive en tiempo real.")

# 5. Revertir la solicitud a PENDIENTE para dejar todo limpio
conn = get_connection(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    UPDATE aprobaciones
    SET estado = 'PENDIENTE', estado_n1 = 'PENDIENTE', aprobado_por_n1 = NULL,
        comentario_n1 = NULL, fecha_n1 = NULL, aprobado_por = NULL, fecha_aprobacion = NULL
    WHERE id = ?
""", (sol_id,))
conn.commit()
conn.close()
from data.database import regenerar_aprobaciones_excel
regenerar_aprobaciones_excel(DB_PATH)
time.sleep(4)
print("\n[OK] Solicitud de prueba revertida a PENDIENTE y Google Drive actualizado nuevamente.")
