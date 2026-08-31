import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gdrive_uploader import _get_drive_service, DRIVE_FOLDER_ID

service = _get_drive_service()
query = f"'{DRIVE_FOLDER_ID}' in parents and trashed = false"
res = service.files().list(q=query, fields='files(id, name, modifiedTime)', supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
files = res.get('files', [])
print("Archivos encontrados en Google Drive (AGOSTO):")
for f in files:
    print(f" - {f['name']} (ID: {f['id']}, Modificado: {f['modifiedTime']})")
