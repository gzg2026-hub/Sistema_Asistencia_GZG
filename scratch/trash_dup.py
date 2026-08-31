import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gdrive_uploader import _get_drive_service, DRIVE_FOLDER_ID

service = _get_drive_service()
try:
    res = service.files().update(
        fileId='1ulAvvDepLQc9QZVbT097Ze6Fl76bHXKn',
        body={'trashed': True},
        supportsAllDrives=True
    ).execute()
    print("Éxito enviando a la papelera:", res)
except Exception as e:
    print(f"Error trashed: {e}")
    # Try removing parent
    try:
        res = service.files().update(
            fileId='1ulAvvDepLQc9QZVbT097Ze6Fl76bHXKn',
            removeParents=DRIVE_FOLDER_ID,
            supportsAllDrives=True
        ).execute()
        print("Éxito removiendo de la carpeta AGOSTO:", res)
    except Exception as e2:
        print(f"Error removeParents: {e2}")
