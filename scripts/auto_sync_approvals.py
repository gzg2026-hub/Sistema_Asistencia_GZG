"""
auto_sync_approvals.py
======================
Servicio de monitoreo y sincronización automática del Excel de Aprobaciones desde Google Drive hacia la PC local.
- Consulta Google Drive cada 45 segundos de manera ultra-ligera (inspeccionando modifiedTime).
- Soporta múltiples meses (mes en curso y mes previo para días de cierre contable).
- Solo descarga y rehidrata cuando detecta cambios reales en la nube (firmas/sustentos móviles).
- Si el archivo Excel está abierto en la PC (bloqueado por Windows), maneja la excepción limpiamente y reintenta.
- Puede ejecutarse como demonio continuo en segundo plano o puntualmente con '--once'.
"""

import os
import sys
import time
import datetime
import traceback

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from scripts.gdrive_uploader import _get_drive_service, DRIVE_FOLDER_ID, DRIVE_MONTH_FOLDERS, descargar_archivo_de_gdrive
from data.database import sincronizar_aprobaciones_con_gdrive, DB_PATH

LOG_FILE = os.path.join(ROOT_DIR, "logs", "auto_sync_approvals.log")

# Proteger contra NoneType en stdout/stderr cuando se ejecuta con pythonw.exe en Windows
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

def log_sync(msg: str):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [AprobacionesSync] {msg}"
    try:
        if sys.stdout and not sys.stdout.closed:
            print(line, flush=True)
    except Exception:
        pass
    try:
        # Rotar log si supera 5 MB
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 5 * 1024 * 1024:
            bk_log = LOG_FILE + ".old"
            if os.path.exists(bk_log):
                os.remove(bk_log)
            os.rename(LOG_FILE, bk_log)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def obtener_meses_relevantes():
    """Retorna lista de meses a monitorear: [mes_actual, mes_previo]."""
    try:
        from zoneinfo import ZoneInfo
        ahora = datetime.datetime.now(ZoneInfo("America/Lima"))
    except Exception:
        ahora = datetime.datetime.now()
    
    mes_actual = ahora.strftime("%Y-%m")
    dt_prev = (ahora.replace(day=1) - datetime.timedelta(days=1))
    mes_previo = dt_prev.strftime("%Y-%m")
    return [mes_actual, mes_previo]


def consultar_metadatos_drive(service):
    """Consulta la lista de archivos de aprobaciones en Drive (en AGOSTO y SETIEMBRE) y sus fechas de modificación."""
    if not service:
        return {}
    try:
        fids = list(set(DRIVE_MONTH_FOLDERS.values()))
        parent_cond = " or ".join([f"'{fid}' in parents" for fid in fids])
        query = f"({parent_cond}) and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name, modifiedTime, size)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get("files", [])
        mapa_archivos = {}
        for f in files:
            name = f.get("name", "")
            if name.lower().startswith("aprobaciones_gzg_") and name.lower().endswith(".xlsx"):
                mapa_archivos[name] = {
                    "id": f.get("id"),
                    "modifiedTime": f.get("modifiedTime"),
                    "size": f.get("size")
                }
        return mapa_archivos
    except Exception as e:
        log_sync(f"Aviso consultando metadatos de Drive: {e}")
        return {}


def sincronizar_un_mes(nombre_archivo: str, sa_dict: dict = None) -> bool:
    """Descarga el archivo y rehidrata la base SQLite local."""
    local_path = os.path.join(ROOT_DIR, "downloads", "data_procesada", nombre_archivo)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    ok_dl = descargar_archivo_de_gdrive(nombre_archivo, local_path, sa_dict=sa_dict)
    if ok_dl:
        try:
            sincronizar_aprobaciones_con_gdrive(DB_PATH)
            tam = os.path.getsize(local_path) if os.path.exists(local_path) else 0
            log_sync(f"Éxito: {nombre_archivo} actualizado y rehidratado en PC local ({tam:,} bytes).")
            return True
        except Exception as e_db:
            log_sync(f"Aviso rehidratando SQLite para {nombre_archivo}: {e_db}")
            return True
    return False


def ejecutar_sincronizacion_completa(forzar: bool = False, cache_modtimes: dict = None) -> dict:
    """
    Revisa Drive y sincroniza únicamente los archivos modificados o todos si forzar=True.
    Retorna el diccionario actualizado de cache_modtimes.
    """
    if cache_modtimes is None:
        cache_modtimes = {}
    
    service = _get_drive_service()
    if not service:
        log_sync("No se pudo conectar a Google Drive API.")
        return cache_modtimes

    mapa_drive = consultar_metadatos_drive(service)
    meses = obtener_meses_relevantes()

    for m in meses:
        nombre = f"Aprobaciones_GZG_{m}.xlsx"
        if nombre in mapa_drive:
            remote_mod = mapa_drive[nombre].get("modifiedTime")
            local_path = os.path.join(ROOT_DIR, "downloads", "data_procesada", nombre)
            
            debe_sincronizar = False
            if forzar:
                debe_sincronizar = True
            elif not os.path.exists(local_path):
                debe_sincronizar = True
            elif cache_modtimes.get(nombre) != remote_mod:
                debe_sincronizar = True

            if debe_sincronizar:
                log_sync(f"Detectado cambio en Drive para {nombre} (ModTime: {remote_mod}). Descargando...")
                try:
                    sincronizar_un_mes(nombre)
                    cache_modtimes[nombre] = remote_mod
                except PermissionError:
                    log_sync(f"BLOQUEADO: {nombre} está abierto en Microsoft Excel. Ciérrelo para actualizar.")
                except Exception as ex:
                    log_sync(f"Error descargando {nombre}: {ex}")
    
    return cache_modtimes


def bucle_demonio(intervalo_segundos: int = 45):
    """Bucle continuo en segundo plano con control de errores."""
    log_sync(f"Iniciando servicio de sincronización continua de Aprobaciones (cada {intervalo_segundos}s)...")
    cache_mod = {}
    
    # Primera sincronización forzada al arrancar
    try:
        cache_mod = ejecutar_sincronizacion_completa(forzar=True, cache_modtimes=cache_mod)
    except Exception as e_init:
        log_sync(f"Aviso en sincronización inicial: {e_init}")

    while True:
        try:
            time.sleep(intervalo_segundos)
            cache_mod = ejecutar_sincronizacion_completa(forzar=False, cache_modtimes=cache_mod)
        except Exception as e_loop:
            log_sync(f"Error en ciclo de sincronización: {e_loop}")
            time.sleep(10)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] in ("--once", "-1", "once"):
            log_sync("Ejecución puntual manual solicitada...")
            ejecutar_sincronizacion_completa(forzar=True)
            print("\nSincronización completada exitosamente.")
        else:
            bucle_demonio(intervalo_segundos=45)
    except Exception as e_main:
        log_sync(f"CRASH NO CONTROLADO: {e_main}\n{traceback.format_exc()}")