from google.oauth2 import service_account
from googleapiclient.discovery import build
import os, json

key_file = 'gzg-asistencia-system-91d54f4af312.json'
try:
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    query = "'1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU' in parents and trashed = false"
    res = service.files().list(q=query, fields='files(id, name, modifiedTime)', supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    files = res.get('files', [])
    print("CONEXION 100% EXITOSA CON GOOGLE DRIVE!")
    print(f"Total de archivos en carpeta AGOSTO: {len(files)}")
    for f in files:
        print(f" - {f['name']} (Modificado: {f.get('modifiedTime')})")
except Exception as e:
    print(f"ERROR: {e}")
