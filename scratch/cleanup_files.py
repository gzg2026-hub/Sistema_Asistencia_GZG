import os
import datetime

hoy_str = datetime.date.today().strftime("%Y-%m-%d")
d_raw = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda"
d_proc = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\diario"

# 1. Eliminar archivo diario del día de hoy (incompleto)
p_hoy = os.path.join(d_proc, f"Reporte_Asistencia_GZG_{hoy_str}.xlsx")
if os.path.exists(p_hoy):
    try:
        os.remove(p_hoy)
        print(f"Eliminado archivo incompleto del día de hoy: {p_hoy}")
    except Exception as e:
        print(f"Aviso al eliminar {p_hoy}: {e}")

# 2. Conservar únicamente Transacciones_Acumuladas.xlsx en data_cruda
if os.path.exists(d_raw):
    for f in os.listdir(d_raw):
        if f != "Transacciones_Acumuladas.xlsx":
            p = os.path.join(d_raw, f)
            try:
                os.remove(p)
                print(f"Eliminado archivo raw temporal: {f}")
            except Exception as e:
                print(f"Aviso al eliminar {f}: {e}")

print("\n--- Estado de downloads/data_cruda ---")
if os.path.exists(d_raw):
    for f in os.listdir(d_raw):
        print(f"  - {f}")

print("\n--- Estado de downloads/data_procesada/diario ---")
if os.path.exists(d_proc):
    for f in sorted(os.listdir(d_proc)):
        print(f"  - {f}")
