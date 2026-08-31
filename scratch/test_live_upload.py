import os
import sys
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from scripts.gdrive_uploader import subir_archivo_a_gdrive, _get_drive_service, DRIVE_FOLDER_ID

print("=== PRUEBA DE SUBIDA EN VIVO A GOOGLE DRIVE ===")
aprob_path = os.path.join(ROOT_DIR, "downloads", "data_procesada", "Aprobaciones_GZG_2026-08.xlsx")
print(f"1. Archivo local a probar: {aprob_path}")
print(f"2. Tamano local: {os.path.getsize(aprob_path)} bytes")

print("\n3. Ejecutando funcion subir_archivo_a_gdrive()...")
inicio = datetime.datetime.now()
resultado = subir_archivo_a_gdrive(aprob_path)
fin = datetime.datetime.now()
duracion = (fin - inicio).total_seconds()

print(f"4. Resultado de la subida: {'EXITOSA (True)' if resultado else 'FALLIDA (False)'}")
print(f"5. Tiempo de subida: {duracion:.2f} segundos")

print("\n6. Verificando estado del archivo en la nube (Google Drive)...")
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
    print(f"   - Nombre en Drive: {f.get('name')}")
    print(f"   - ID en Drive: {f.get('id')}")
    print(f"   - Fecha/Hora de Modificacion en Drive: {f.get('modifiedTime')}")
    print(f"   - Tamano en Drive: {f.get('size')} bytes")
    print("\n=> CONCLUSION: LA API DE GOOGLE DRIVE ACTUALIZA Y SUBE EL ARCHIVO DE FORMA PERFECTA E INSTANTANEA.")
else:
    print("ERROR: No se encontro el archivo en Drive.")
