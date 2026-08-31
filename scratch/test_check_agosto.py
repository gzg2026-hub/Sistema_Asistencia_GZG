import os, sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from scripts.gdrive_uploader import _get_drive_service, DRIVE_FOLDER_ID

service = _get_drive_service()
query = f"'{DRIVE_FOLDER_ID}' in parents and trashed = false"
res = service.files().list(
    q=query,
    fields="files(id, name, modifiedTime, size)",
    supportsAllDrives=True,
    includeItemsFromAllDrives=True
).execute()

print("=== ARCHIVOS ACTUALES EN CARPETA AGOSTO (GOOGLE DRIVE) ===")
for f in res.get("files", []):
    sz = int(f.get("size", 0)) / 1024 if f.get("size") else 0
    print(f" - {f['name']} | {sz:.1f} KB | Modificado: {f.get('modifiedTime')} | ID: {f['id']}")
