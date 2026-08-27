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


def subir_archivo_a_gdrive(local_file_path: str, subfolder_name: str = "", sa_dict: dict = None) -> bool:
    """
    Sube o actualiza un archivo local en la carpeta compartida de Google Drive (ID: 1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU).
    EXCEPCIÓN AUTORIZADA POR EL USUARIO:
      1. Transacciones_Acumuladas.xlsx
      2. Reporte_Asistencia_GZG_YYYY-MM-DD.xlsx (Reportes diarios cerrados)
      3. Aprobaciones_GZG_YYYY-MM.xlsx (triggered inmediatamente tras cada accion de aprobacion/rechazo)
    PROHIBICIÓN STRICTA:
      - Sistema_Asistencia_GZG_v1.0.xlsx (Permanentemente local en PC)
    """
    if not os.path.exists(local_file_path):
        log_drive(f"Error: El archivo local no existe -> {local_file_path}")
        return False

    file_name = os.path.basename(local_file_path).strip()
    file_name_lower = file_name.lower()

    es_transacciones = (file_name_lower == "transacciones_acumuladas.xlsx")
    es_reporte_diario = file_name_lower.startswith("reporte_asistencia_gzg_") and file_name_lower.endswith(".xlsx")
    es_aprobaciones = file_name_lower.startswith("aprobaciones_gzg_") and file_name_lower.endswith(".xlsx")

    if not (es_transacciones or es_reporte_diario or es_aprobaciones):
        log_drive(f"DENEGADO: El archivo '{file_name}' no pertenece a los 3 autorizados para Google Drive. Permanece exclusivo en PC.")
        return False

    log_drive(f"Iniciando subida autorizada de {file_name} a Google Drive (Folder ID: {DRIVE_FOLDER_ID})...")
    try:
        from googleapiclient.http import MediaFileUpload
        service = _get_drive_service(sa_dict=sa_dict)
        if not service:
            log_drive("Error: No se pudo autenticar con Google Drive API")
            return False

        query = f"'{DRIVE_FOLDER_ID}' in parents and name = '{file_name}' and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get("files", [])

        media = MediaFileUpload(local_file_path, resumable=True)

        if files:
            file_id = files[0]["id"]
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media,
                supportsAllDrives=True,
                fields="id, name"
            ).execute()
            log_drive(f"Éxito: Archivo actualizado por API (ID: {updated_file.get('id')}) -> {file_name}")
        else:
            file_metadata = {"name": file_name, "parents": [DRIVE_FOLDER_ID]}
            created_file = service.files().create(
                body=file_metadata,
                media_body=media,
                supportsAllDrives=True,
                fields="id, name"
            ).execute()
            log_drive(f"Éxito: Archivo creado por API (ID: {created_file.get('id')}) -> {file_name}")

        return True
    except Exception as e:
        log_drive(f"Aviso API Google Drive: {e}")
        return False


def _get_drive_service(sa_dict: dict = None):
    """Construye y retorna el cliente oficial de Google Drive v3 con credenciales seguras."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        creds = None

        # 0. Si se pasó sa_dict explícito (ej. desde hilo principal seguro)
        if sa_dict:
            try:
                creds = service_account.Credentials.from_service_account_info(
                    sa_dict,
                    scopes=["https://www.googleapis.com/auth/drive"]
                )
            except Exception:
                pass
        
        # 1. En Streamlit Cloud, priorizar siempre st.secrets["gcp_service_account"]
        if not creds:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
                    creds = service_account.Credentials.from_service_account_info(
                        dict(st.secrets["gcp_service_account"]),
                        scopes=["https://www.googleapis.com/auth/drive"]
                    )
            except Exception:
                pass

        # 2. En PC local, intentar credentials.json si no hay st.secrets
        if not creds:
            creds_path = os.path.join(ROOT_DIR, "credentials.json")
            if os.path.exists(creds_path):
                try:
                    creds = service_account.Credentials.from_service_account_file(
                        creds_path, scopes=["https://www.googleapis.com/auth/drive"]
                    )
                except Exception as e_cf:
                    log_drive(f"Aviso lectura credentials.json: {e_cf}")

        if creds:
            return build("drive", "v3", credentials=creds)
    except Exception as e:
        log_drive(f"Error inicializando Google Drive API: {e}")
    return None


def descargar_archivo_de_gdrive(file_name: str, local_dest_path: str, sa_dict: dict = None) -> bool:
    """Descarga un archivo específico desde la carpeta compartida de Google Drive si existe."""
    try:
        service = _get_drive_service(sa_dict=sa_dict)
        if not service:
            return False
        
        query = f"'{DRIVE_FOLDER_ID}' in parents and name = '{file_name}' and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get("files", [])
        if not files:
            return False
        
        file_id = files[0]["id"]
        from googleapiclient.http import MediaIoBaseDownload
        import io
        request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
        dest_dir = os.path.dirname(local_dest_path)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)
        with io.FileIO(local_dest_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        log_drive(f"Éxito: Archivo descargado desde Drive -> {file_name}")
        return True
    except Exception as e:
        log_drive(f"Aviso descarga Drive ({file_name}): {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        f_path = sys.argv[1]
        subir_archivo_a_gdrive(f_path)
    else:
        log_drive("Ejecutar con parámetro: python gdrive_uploader.py <ruta_archivo>")
