import os

root_dir = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"

unused_files = [
    "test_clean.xlsx",
    "test_out.xlsm",
    "test_valid.xlsx",
    "Sistema_Asistencia_GZG_v1.0_HHMM.xlsx",
    "Sistema_Asistencia_GZG_v1.0_procesado.xlsm"
]

for fname in unused_files:
    fpath = os.path.join(root_dir, fname)
    if os.path.exists(fpath):
        try:
            os.remove(fpath)
            print(f"[OK] Eliminado archivo de prueba: {fname}")
        except Exception as e:
            print(f"[ERR] No se pudo eliminar {fname}: {e}")
    else:
        print(f"[INFO] Archivo no existía: {fname}")
