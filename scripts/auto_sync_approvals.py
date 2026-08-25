"""
auto_sync_approvals.py
======================
Daemon en segundo plano que sincroniza en tiempo real las aprobaciones
realizadas desde el app móvil (Streamlit Cloud) hacia:
  1. Base de datos SQLite local (data/asistencia.db)
  2. Excel local de Aprobaciones (downloads/data_procesada/Aprobaciones_GZG_YYYY-MM.xlsx)
  3. Google Drive (carpeta AGOSTO)
"""

import os
import sys
import time
import subprocess
import datetime
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import DB_PATH, regenerar_aprobaciones_excel, get_connection
from data.exporter import exportar_aprobaciones_excel

def log_sync(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [AutoSync] {msg}", flush=True)

def sync_from_remote_repo():
    """Hace git pull silencioso para traer aprobaciones hechas desde la nube."""
    try:
        res = subprocess.run(
            ["git", "pull", "origin", "main", "--no-rebase"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=15
        )
        if "Already up to date" not in res.stdout and "Ya está actualizado" not in res.stdout:
            log_sync(f"Nuevas actualizaciones recibidas desde el app: {res.stdout.strip()}")
            regenerar_aprobaciones_excel(DB_PATH)
            return True
    except Exception as e:
        pass
    return False

def sync_cycle():
    log_sync("Iniciando daemon de sincronización automática en tiempo real...")
    while True:
        try:
            hubo_cambio = sync_from_remote_repo()
            if hubo_cambio:
                log_sync("Excel local de Aprobaciones actualizado exitosamente con las acciones del app.")
        except Exception as e:
            pass
        time.sleep(10)

if __name__ == "__main__":
    sync_cycle()
