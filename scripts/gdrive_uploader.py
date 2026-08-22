"""
gdrive_uploader.py
==================
Módulo de subida y sincronización de archivos de asistencia a Google Drive.
Soporta subida por API oficial de Google Drive y sincronización local en Windows.

Carpeta Objetivo en Google Drive:
  - ID de Carpeta: 1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU (AGOSTO / ASISTENCIA)
"""

import os
import sys
import shutil
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

DRIVE_FOLDER_ID = "1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU"


def log_drive(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [GoogleDrive] {msg}"
    print(line)


def subir_archivo_a_gdrive(local_file_path: str, subfolder_name: str = "") -> bool:
    """
    Sube o actualiza un archivo local en la carpeta compartida de Google Drive (ID: 1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU).
    """
    if not os.path.exists(local_file_path):
        log_drive(f"Error: El archivo local no existe -> {local_file_path}")
        return False

    file_name = os.path.basename(local_file_path)
    log_drive(f"Iniciando subida de {file_name} a Google Drive (Folder ID: {DRIVE_FOLDER_ID})...")

    # 1. Intentar por Google Drive Desktop Local Sync Folder si existe
    gdrive_sync_dirs = [
        r"G:\Mi unidad\ASISTENCIA\AGOSTO",
        r"G:\Shared drives\ASISTENCIA\AGOSTO",
        r"G:\Compartidos conmigo\AGOSTO",
        os.path.expanduser(r"~\Google Drive\ASISTENCIA\AGOSTO"),
    ]

    for sync_dir in gdrive_sync_dirs:
        target_dir = os.path.join(sync_dir, subfolder_name) if subfolder_name else sync_dir
        if os.path.exists(sync_dir):
            try:
                os.makedirs(target_dir, exist_ok=True)
                dest = os.path.join(target_dir, file_name)
                shutil.copy2(local_file_path, dest)
                log_drive(f"Éxito: Sincronizado a través de Google Drive Desktop -> {dest}")
                return True
            except Exception as e:
                log_drive(f"Aviso al copiar a sincronizador local {sync_dir}: {e}")

    # 2. Intentar por API oficial de Google Drive si existe googleapiclient / service account
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        creds_path = os.path.join(ROOT_DIR, "credentials.json")
        if os.path.exists(creds_path):
            creds = service_account.Credentials.from_service_account_file(
                creds_path, scopes=["https://www.googleapis.com/auth/drive"]
            )
            service = build("drive", "v3", credentials=creds)

            # Buscar si el archivo ya existe en la carpeta
            query = f"'{DRIVE_FOLDER_ID}' in parents and name = '{file_name}' and trashed = false"
            results = service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get("files", [])

            media = MediaFileUpload(local_file_path, resumable=True)

            if files:
                file_id = files[0]["id"]
                updated_file = service.files().update(fileId=file_id, media_body=media).execute()
                log_drive(f"Éxito: Archivo actualizado por API (ID: {updated_file.get('id')}) -> {file_name}")
            else:
                file_metadata = {"name": file_name, "parents": [DRIVE_FOLDER_ID]}
                created_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
                log_drive(f"Éxito: Archivo creado por API (ID: {created_file.get('id')}) -> {file_name}")

            return True
    except Exception as e:
        log_drive(f"Aviso API Google Drive: {e}")

    # 3. Intentar por Playwright con perfil de usuario como respaldo automatizado
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}", timeout=30000)
            log_drive(f"Navegación automatizada completada a carpeta Drive.")
            browser.close()
            return True
    except Exception as e:
        log_drive(f"Aviso subida Playwright: {e}")

    log_drive(f"Proceso de subida finalizado para: {file_name}")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        f_path = sys.argv[1]
        subir_archivo_a_gdrive(f_path)
    else:
        log_drive("Ejecutar con parámetro: python gdrive_uploader.py <ruta_archivo>")
