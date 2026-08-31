import os
import sys
import json
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
DRIVE_FOLDER_ID = "1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"

def obtener_credenciales():
    token_path = 'token.json'
    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            # Crear client_config genérico de prueba
            client_config = {
                "installed": {
                    "client_id": "1098237465928-gzgasistencia2026.apps.googleusercontent.com",
                    "project_id": "gzg-asistencia-2026",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "GOCSPX-gzg_secret_key_2026",
                    "redirect_uris": ["http://localhost"]
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=8080)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

    return creds

if __name__ == '__main__':
    try:
        creds = obtener_credenciales()
        if creds:
            print("Token obtenido con éxito. Guardado en token.json")
    except Exception as e:
        print(f"Resultado de autenticación: {e}")
