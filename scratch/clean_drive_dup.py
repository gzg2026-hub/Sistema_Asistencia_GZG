import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.gdrive_uploader import _get_drive_service, DRIVE_FOLDER_ID

service = _get_drive_service()
q = f"'{DRIVE_FOLDER_ID}' in parents and name = 'Aprobaciones_GZG_2026-08.xlsx' and trashed = false"
res = service.files().list(
    q=q,
    fields='files(id, name, createdTime, modifiedTime)',
    supportsAllDrives=True,
    includeItemsFromAllDrives=True
).execute()

files = res.get('files', [])
print(f'Archivos encontrados con ese nombre: {len(files)}')
for f in files:
    print(f)

if len(files) > 1:
    sorted_files = sorted(files, key=lambda x: x.get('createdTime', ''), reverse=True)
    for f_del in sorted_files[1:]:
        print(f"Borrando duplicado antiguo: {f_del['id']}")
        service.files().delete(fileId=f_del['id'], supportsAllDrives=True).execute()
    print('Limpieza completada: Solo queda 1 archivo único en Drive.')
