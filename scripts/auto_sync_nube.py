import os
import sys
import time
import subprocess
import datetime

def sincronizar_desde_nube():
    """Descarga e integra automáticamente los cambios realizados en GitHub hacia la PC local."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    try:
        res = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, timeout=30)
        if res.returncode == 0 and "Already up to date" not in res.stdout:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] ☁️ ¡Nuevos datos descargados automáticamente desde GitHub!")
            print(res.stdout.strip())
    except Exception as e:
        print(f"[Sync Warning] No se pudo verificar la nube: {e}")

def iniciar_auto_sync(intervalo_segundos: int = 300):
    print("🔄 Servicio de Sincronización Automática (Nube -> PC) Activo.")
    print(f"   Verificando e importando cambios de GitHub cada {intervalo_segundos // 60} minutos...")
    sincronizar_desde_nube()
    while True:
        time.sleep(intervalo_segundos)
        sincronizar_desde_nube()

if __name__ == '__main__':
    iniciar_auto_sync()
