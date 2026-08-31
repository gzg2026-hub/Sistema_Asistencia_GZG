import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gdrive_uploader import _get_drive_service, DRIVE_FOLDER_ID

service = _get_drive_service()
q = f"'{DRIVE_FOLDER_ID}' in parents and trashed = false"
res = service.files().list(
    q=q,
    fields='files(id, name, createdTime)',
    supportsAllDrives=True,
    includeItemsFromAllDrives=True
).execute()

print(f"Total archivos en AGOSTO: {len(res.get('files', []))}")
for f in res.get('files', []):
    print(f"{f['name']:<45} | ID: {f['id']}")
