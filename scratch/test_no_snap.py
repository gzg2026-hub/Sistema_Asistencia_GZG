import os
import sys
import pandas as pd

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

# Vamos a probar modificar el calculo de e_effective_sec para usar la hora REAL de entrada
with open(os.path.join(PROJECT_ROOT, "core", "attendance_engine.py"), "r", encoding="utf-8") as f:
    code = f.read()

# Reemplazar la logica de e_effective_sec que forzaba 07:00 / 19:00 por la hora REAL de entrada (e_sec)
target_block = """                e_effective_sec = e_sec
                if 6 * 3600 <= e_sec < 7 * 3600:
                    e_effective_sec = 7 * 3600
                elif 18 * 3600 <= e_sec < 19 * 3600:
                    e_effective_sec = 19 * 3600
                elif 4 * 3600 <= e_sec < 5 * 3600:
                    e_effective_sec = 5 * 3600
                elif 16 * 3600 <= e_sec < 17 * 3600:
                    e_effective_sec = 17 * 3600"""

replacement_block = """                # Usar marcación REAL de entrada (sin forzar inicio oficial) para calcular el tiempo total transcurrido
                e_effective_sec = e_sec"""

if target_block in code:
    code_mod = code.replace(target_block, replacement_block)
    with open(os.path.join(PROJECT_ROOT, "core", "attendance_engine.py"), "w", encoding="utf-8") as f:
        f.write(code_mod)
    print("Modificado core/attendance_engine.py para usar marcacion REAL de entrada.")
else:
    print("No se encontro el bloque target.")
