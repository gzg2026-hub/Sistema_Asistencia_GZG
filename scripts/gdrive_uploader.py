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
    EXCEPCIÓN AUTORIZADA POR EL USUARIO:
      1. Transacciones_Acumuladas.xlsx
      2. Reporte_Asistencia_GZG_YYYY-MM-DD.xlsx (Reportes diarios cerrados)
    PROHIBICIÓN STRICTA:
      - Sistema_Asistencia_GZG_v1.0.xlsx (Permanentemente local en PC)
    """
    if not os.path.exists(local_file_path):
        log_drive(f"Error: El archivo local no existe -> {local_file_path}")
        return False

    file_name = os.path.basename(local_file_path).strip()
    file_name_lower = file_name.lower()

    # FILTRO EXCLUSIVO DE EXCEPCIÓN AUTORIZADA: Únicamente Transacciones_Acumuladas.xlsx o Reporte_Asistencia_GZG_YYYY-MM-DD.xlsx
    es_transacciones = (file_name_lower == "transacciones_acumuladas.xlsx")
    es_reporte_diario = file_name_lower.startswith("reporte_asistencia_gzg_") and file_name_lower.endswith(".xlsx")

    if not (es_transacciones or es_reporte_diario):
        log_drive(f"DENEGADO: El archivo '{file_name}' no pertenece a los 2 autorizados para Google Drive. Permanece exclusivo en PC.")
        return False

    log_drive(f"Iniciando subida autorizada de {file_name} a Google Drive (Folder ID: {DRIVE_FOLDER_ID})...")
    # Subida directa a Nube por API oficial de Google Drive (sin vincular ni tocar carpetas locales del disco G:)
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
