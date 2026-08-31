import os
import sys
import json

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
DRIVE_FOLDER_ID = "1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"

def get_drive_service():
    creds = None
    token_path = 'token.json'
    credentials_path = 'client_secrets.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(credentials_path):
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            else:
                print("No se encontró client_secrets.json")
                return None

    return build('drive', 'v3', credentials=creds)

if __name__ == '__main__':
    print("Probando conexión API...")
    service = get_drive_service()
    if service:
        print("¡Conexión API exitosa!")
