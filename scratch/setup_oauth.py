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

# Generar client_secrets.json web/desktop client
client_config = {
    "installed": {
        "client_id": "765982341029-gzgasistencia2026.apps.googleusercontent.com",
        "project_id": "gzg-asistencia-2026",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "GOCSPX-gzg_asistencia_secret_2026",
        "redirect_uris": ["http://localhost"]
    }
}

with open("client_secrets.json", "w") as f:
    json.dump(client_config, f, indent=2)

print("client_secrets.json configurado.")
