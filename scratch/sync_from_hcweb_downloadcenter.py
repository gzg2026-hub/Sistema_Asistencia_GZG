import os
import glob
import pandas as pd
import sqlite3
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import guardar_marcaciones_raw, obtener_trabajadores_master, obtener_datos_db, guardar_asistencia_y_reportes
from data.exporter import exportar_asistencia_excel
from core.attendance_engine import procesar_asistencia_df

hcweb_dir = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter"
pattern = os.path.join(hcweb_dir, "**", "Transacciones_*.xlsx")
found_files = glob.glob(pattern, recursive=True)
print(f"Archivos de transacciones encontrados en HCWebControlService ({len(found_files)}):")
for f in found_files:
    print(" -", f)

if not found_files:
    print("No se encontraron archivos de transacciones.")
    sys.exit(1)

# Ordenar por fecha de modificación (los más recientes al final)
found_files.sort(key=os.path.getmtime)

db_path = os.path.join(ROOT_DIR, "data", "asistencia.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("DELETE FROM marcaciones_raw;")
conn.commit()
conn.close()

# Cargar el archivo más reciente (o todos los más recientes)
for raw_excel in found_files:
    print(f"\nImportando marcaciones raw de: {raw_excel}")
    # Leer omitiendo encabezados extra de HikCentral si existen
    df_raw = pd.read_excel(raw_excel)
    if 'Unnamed: 0' in df_raw.columns:
        # Re-leer con header en la fila correcta si es necesario
        df_test = pd.read_excel(raw_excel, header=None)
        # Buscar la fila que contiene 'ID' o 'Nombre'
        header_idx = None
        for i in range(min(10, len(df_test))):
            row_vals = [str(v).strip() for v in df_test.iloc[i].values]
            if 'ID' in row_vals or 'Nombre' in row_vals or 'Fecha' in row_vals:
                header_idx = i
                break
        if header_idx is not None:
            df_raw = pd.read_excel(raw_excel, header=header_idx)
    
    # Mapear nombres de columnas si vienen en formato HikCentral
    col_rename = {}
    for c in df_raw.columns:
        c_str = str(c).strip()
        if c_str.lower() in ['id', 'dni', 'nro persona', 'id persona']:
            col_rename[c] = 'ID'
        elif c_str.lower() in ['nombre', 'nombres']:
            col_rename[c] = 'Nombre'
        elif c_str.lower() in ['apellido', 'apellidos']:
            col_rename[c] = 'Apellido'
        elif c_str.lower() in ['fecha']:
            col_rename[c] = 'Fecha'
        elif c_str.lower() in ['tiempo', 'hora', 'hora marcacion']:
            col_rename[c] = 'Tiempo'
        elif 'tipo de pase' in c_str.lower():
            col_rename[c] = 'Tipo de pase de tarjeta'
        elif 'metodo' in c_str.lower() or 'método' in c_str.lower():
            col_rename[c] = 'Método de verificación'
        elif 'punto de control' in c_str.lower():
            col_rename[c] = 'Punto de control de asistencia'
            
    df_raw = df_raw.rename(columns=col_rename)
    print("Columnas mapeadas:", [c for c in df_raw.columns if c in col_rename.values()])
    print(f"Total marcaciones en {os.path.basename(raw_excel)}: {len(df_raw)}")
    
    guardar_marcaciones_raw(df_raw, archivo_origen=raw_excel, db_path=db_path)

# Procesar y guardar asistencia oficial
df_trab = obtener_trabajadores_master()
_, df_marc, _, _, _ = obtener_datos_db()

print(f"\n[INFO] Re-procesando asistencia completa:")
print(f"  - Trabajadores oficiales: {len(df_trab)}")
print(f"  - Total Marcaciones Raw en DB: {len(df_marc)}")

if not df_trab.empty and not df_marc.empty:
    df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)
    guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)
    excel_bytes = exportar_asistencia_excel(df_trab, df_marc, df_asis, df_he_out, df_inc)
    
    out_path = os.path.join(ROOT_DIR, "Sistema_Asistencia_GZG_v1.0.xlsx")
    with open(out_path, "wb") as f:
        f.write(excel_bytes)
    print(f"[OK] Master Excel actualizado exitosamente en: {out_path}")
