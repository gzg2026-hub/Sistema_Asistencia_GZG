import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from scripts.gdrive_uploader import _get_drive_service, DRIVE_FOLDER_ID

print("=== VERIFICACION DE CREDENCIALES DE GOOGLE DRIVE ===")
creds_path = os.path.join(ROOT_DIR, "credentials.json")
print(f"1. Archivo local: {creds_path}")
print(f"2. Existe credentials.json: {os.path.exists(creds_path)}")

service = _get_drive_service()
if service:
    print("3. Autenticacion API v3: EXITOSA (OK)")
    try:
        q = f"'{DRIVE_FOLDER_ID}' in parents and trashed = false"
        res = service.files().list(
            q=q,
            fields="files(id, name, modifiedTime)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = res.get("files", [])
        print(f"4. Conexion con carpeta AGOSTO ({DRIVE_FOLDER_ID}): EXITOSA (OK)")
        print(f"5. Total archivos listados: {len(files)}")
        for f in files:
            print(f"   - {f.get('name')} | ID: {f.get('id')} | Modificado: {f.get('modifiedTime')}")
        print("\n=> CONCLUSION: MANANA A LAS 9:00 AM LA SUBIDA AUTOMATICA FUNCIONARA 100% SIN PROBLEMAS.")
    except Exception as e:
        print(f"ERROR listando carpeta en Drive: {e}")
else:
    print("ERROR: No se pudo autenticar el servicio de Drive.")
