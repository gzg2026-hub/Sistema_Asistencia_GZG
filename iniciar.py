import os
import sys
import subprocess

if __name__ == "__main__":
    # Obtener el directorio actual del script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    app_path = os.path.join(base_dir, "app.py")
    print("Iniciando Sistema de Asistencia GZG...")
    
    # Ejecutar Streamlit usando el mismo interprete de Python
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
