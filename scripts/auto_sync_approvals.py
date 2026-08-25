"""
auto_sync_approvals.py
======================
Descarga puntual (NO sincronización) del Excel de Aprobaciones desde Google Drive.
Solo LEE ese archivo específico — nunca sube nada desde la PC, así que
archivos de prueba locales nunca se filtran hacia Drive.
"""

import os
import sys
import time
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from scripts.gdrive_uploader import descargar_archivo_de_gdrive

def log_sync(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [AprobacionesWatch] {msg}", flush=True)

def descargar_aprobaciones_actual():
    mes_str = datetime.date.today().strftime('%Y-%m')
    nombre_archivo = f"Aprobaciones_GZG_{mes_str}.xlsx"
    destino_local = os.path.join(ROOT_DIR, "downloads", "data_procesada", nombre_archivo)

    ok = descargar_archivo_de_gdrive(nombre_archivo, destino_local)
    if ok:
        log_sync(f"{nombre_archivo} actualizado desde Drive.")
    return ok

def sync_cycle(intervalo_segundos: int = 15):
    log_sync("Iniciando descarga periódica de Aprobaciones (solo lectura desde Drive)...")
    while True:
        try:
            descargar_aprobaciones_actual()
        except Exception as e:
            log_sync(f"Aviso: {e}")
        time.sleep(intervalo_segundos)

if __name__ == "__main__":
    sync_cycle(15)