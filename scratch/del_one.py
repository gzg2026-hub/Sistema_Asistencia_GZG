import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gdrive_uploader import _get_drive_service

service = _get_drive_service()
try:
    service.files().delete(fileId='1ulAvvDepLQc9QZVbT097Ze6Fl76bHXKn', supportsAllDrives=True).execute()
    print("Éxito borrando el duplicado 1ulAvvDepLQc9QZVbT097Ze6Fl76bHXKn")
except Exception as e:
    print(f"Error borrando: {e}")
