from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

try:
    creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    query = "'1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU' in parents and trashed = false"
    res = service.files().list(q=query, fields='files(id, name, modifiedTime)', supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    print("ÉXITO TOTAL: Archivos en Drive con credentials.json:")
    for f in res.get('files', []):
        print(f" - {f['name']} ({f['id']})")
except Exception as e:
    print(f"ERROR con credentials.json: {e}")
