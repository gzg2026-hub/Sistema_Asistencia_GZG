import os
import sys
import shutil

master_raw = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_Acumuladas.xlsx"
diario_dir = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\diario"

# Buscar ruta de sincronización en G:
possible_targets = [
    r"G:\Mi unidad\AGOSTO",
    r"G:\Mi unidad\ASISTENCIA\AGOSTO",
    r"G:\Mi unidad\29. CONECTIVIDAD\ASISTENCIA\AGOSTO",
    r"G:\Compartidos conmigo\AGOSTO",
    r"G:\Compartidos conmigo\29. CONECTIVIDAD\ASISTENCIA\AGOSTO",
    r"G:\Mi unidad",
]

target_dir = None
for p in possible_targets:
    if os.path.exists(p):
        target_dir = p
        break

print(f"Ruta objetivo de Google Drive identificada: {target_dir}")

if not target_dir and os.path.exists(r"G:\Mi unidad"):
    target_dir = r"G:\Mi unidad"

if target_dir:
    # 1. Copiar Data Cruda Maestro Acumulada
    raw_dest_dir = os.path.join(target_dir, "Data_Cruda")
    os.makedirs(raw_dest_dir, exist_ok=True)
    dest_raw_file = os.path.join(raw_dest_dir, "Transacciones_Acumuladas.xlsx")
    shutil.copy2(master_raw, dest_raw_file)
    print(f"[OK] Data Cruda Maestro acumulada copiada a: {dest_raw_file}")

    # 2. Copiar Reportes Procesados Diarios (17 al 21)
    proc_dest_dir = os.path.join(target_dir, "Data_Procesada")
    os.makedirs(proc_dest_dir, exist_ok=True)

    if os.path.exists(diario_dir):
        for f in sorted(os.listdir(diario_dir)):
            if f.endswith(".xlsx") and not f.endswith("2026-08-22.xlsx"):
                src = os.path.join(diario_dir, f)
                dst = os.path.join(proc_dest_dir, f)
                shutil.copy2(src, dst)
                print(f"[OK] Reporte diario procesado completado copiado: {f} -> {dst}")

    print("\n¡Sincronización a Google Drive Desktop completada exitosamente!")
else:
    print("No se encontró ruta de sincronización en G:.")
