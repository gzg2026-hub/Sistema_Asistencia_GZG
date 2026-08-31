import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

client_config = {
    "installed": {
        "client_id": "1098237465928-gzgasistencia2026.apps.googleusercontent.com",
        "project_id": "gzg-asistencia-2026",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "GOCSPX-gzg_secret_key_2026",
        "redirect_uris": ["http://localhost:8080/"]
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
auth_url, _ = flow.authorization_url(prompt='consent')

print("URL_DE_AUTORIZACION_GOOGLE:")
print(auth_url)
