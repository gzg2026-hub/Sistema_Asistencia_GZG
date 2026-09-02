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

DRIVE_PARENT_FOLDER_ID = "1r6IJqsIPiqzqghrNoH6kuorLmR1P45z2"  # Carpeta raíz ASISTENCIA en Google Drive

DRIVE_MONTH_FOLDERS = {
    "08": "1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU",        # AGOSTO
    "agosto": "1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU",
    "09": "1NFC8vDwJGzZqllmT1wS5dgb8X2zyceHn",        # SETIEMBRE
    "setiembre": "1NFC8vDwJGzZqllmT1wS5dgb8X2zyceHn",
    "septiembre": "1NFC8vDwJGzZqllmT1wS5dgb8X2zyceHn",
}

# Carpeta por defecto (compatibilidad con scripts existentes)
DRIVE_FOLDER_ID = DRIVE_MONTH_FOLDERS["08"]


def resolver_folder_id(file_name: str, target_folder: str = "") -> str:
    """Resuelve el ID de carpeta en Drive según el nombre del archivo o mes objetivo."""
    if target_folder:
        tf = str(target_folder).strip().lower()
        if tf in DRIVE_MONTH_FOLDERS:
            return DRIVE_MONTH_FOLDERS[tf]
        return target_folder

    fn_lower = file_name.lower()

    # 1. Por mes explícito en el nombre de archivo (ej. 2026-08 o 2026-09)
    if "2026-08" in fn_lower or "_08_" in fn_lower:
        return DRIVE_MONTH_FOLDERS["08"]
    if "2026-09" in fn_lower or "_09_" in fn_lower:
        return DRIVE_MONTH_FOLDERS["09"]

    # 2. Transacciones_Acumuladas.xlsx va al mes en curso (setiembre en sept, agosto en ago)
    if fn_lower == "transacciones_acumuladas.xlsx":
        hoy = datetime.date.today()
        mes_str = f"{hoy.month:02d}"
        return DRIVE_MONTH_FOLDERS.get(mes_str, DRIVE_MONTH_FOLDERS["09"])

    return DRIVE_MONTH_FOLDERS["09"]


def log_drive(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [GoogleDrive] {msg}"
    print(line)


def subir_archivo_a_gdrive(local_file_path: str, target_folder: str = "", sa_dict: dict = None) -> bool:
    """
    Sube o actualiza un archivo local en la carpeta compartida correspondiente de Google Drive (AGOSTO o SETIEMBRE).
    EXCEPCIÓN AUTORIZADA POR EL USUARIO:
      1. Transacciones_Acumuladas.xlsx
      2. Reporte_Asistencia_GZG_YYYY-MM-DD.xlsx (Reportes diarios cerrados)
      3. Aprobaciones_GZG_YYYY-MM.xlsx (triggered inmediatamente tras cada acción de aprobación/rechazo)
    PROHIBICIÓN ESTRICTA:
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

    folder_id = resolver_folder_id(file_name, target_folder)
    nombre_carpeta = "AGOSTO" if folder_id == DRIVE_MONTH_FOLDERS["08"] else ("SETIEMBRE" if folder_id == DRIVE_MONTH_FOLDERS["09"] else folder_id)

    log_drive(f"Iniciando subida autorizada de {file_name} a Google Drive -> Carpeta: {nombre_carpeta} (ID: {folder_id})...")
    try:
        from googleapiclient.http import MediaFileUpload
        service = _get_drive_service(sa_dict=sa_dict)
        if not service:
            log_drive("Error: No se pudo autenticar con Google Drive API")
            return False

        query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get("files", [])

        media = MediaFileUpload(
            local_file_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=False
        )

        if files:
            file_id = files[0]["id"]
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media,
                supportsAllDrives=True,
                fields="id, name"
            ).execute()
            log_drive(f"Éxito: Archivo actualizado por API en {nombre_carpeta} (ID: {updated_file.get('id')}) -> {file_name}")
        else:
            file_metadata = {"name": file_name, "parents": [folder_id]}
            created_file = service.files().create(
                body=file_metadata,
                media_body=media,
                supportsAllDrives=True,
                fields="id, name"
            ).execute()
            log_drive(f"Éxito: Archivo creado por API en {nombre_carpeta} (ID: {created_file.get('id')}) -> {file_name}")

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


def descargar_archivo_de_gdrive(file_name: str, local_dest_path: str, target_folder: str = "", sa_dict: dict = None) -> bool:
    """Descarga un archivo específico desde la carpeta correspondiente (AGOSTO o SETIEMBRE) de Google Drive si existe."""
    try:
        service = _get_drive_service(sa_dict=sa_dict)
        if not service:
            return False

        folder_id = resolver_folder_id(file_name, target_folder)

        # 1. Buscar en la carpeta objetivo
        query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get("files", [])

        # 2. Si no se encuentra, buscar en las demás carpetas de meses conocidas
        if not files:
            for alt_fid in set(DRIVE_MONTH_FOLDERS.values()):
                if alt_fid == folder_id:
                    continue
                q_alt = f"'{alt_fid}' in parents and name = '{file_name}' and trashed = false"
                res_alt = service.files().list(
                    q=q_alt,
                    fields="files(id, name)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                files = res_alt.get("files", [])
                if files:
                    break

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
