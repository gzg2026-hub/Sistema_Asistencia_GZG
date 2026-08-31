import sys, os
sys.path.insert(0, os.getcwd())
import pandas as pd
from core.attendance_engine import procesar_asistencia_df
from data.exporter import exportar_asistencia_excel
from data.database import sincronizar_aprobaciones_desde_asistencia

print("=== ACTUALIZANDO ARCHIVOS EXCEL DEL SISTEMA ===")

raw_path = os.path.join('downloads', 'data_cruda', 'Transacciones_Acumuladas.xlsx')
padron_path = 'Padron_Trabajadores_GZG.xlsx'
report_23_path = os.path.join('downloads', 'data_procesada', 'diario', 'Reporte_Asistencia_GZG_2026-08-23.xlsx')

# 1. Cargar Data Cruda y Padrón
df_raw = pd.read_excel(raw_path)
df_padron = pd.read_excel(padron_path, header=2)

print(f"[OK] Transacciones Crudas cargadas ({len(df_raw)} filas).")
print(f"[OK] Padrón Trabajadores cargado ({len(df_padron)} trabajadores).")

# 2. Procesar Asistencia con el Motor Corregido
df_asistencia, df_he, df_inc, kpis = procesar_asistencia_df(df_padron, df_raw)

# 3. Filtrar para el día cerrado 23
df_asist_23 = df_asistencia[df_asistencia['FECHA'].astype(str).str.contains('2026-08-23')].copy()

# 4. Generar bytes del reporte 23
excel_bytes = exportar_asistencia_excel(df_padron, df_raw, df_asist_23, df_he, df_inc)

# 5. Guardar Reporte 23
try:
    with open(report_23_path, 'wb') as f:
        f.write(excel_bytes)
    print(f"[EXITO] {report_23_path} guardado y actualizado correctamente.")
except PermissionError:
    print(f"[ADVERTENCIA] No se pudo escribir {report_23_path} porque está abierto en Excel. Por favor ciérrelo.")
except Exception as e:
    print(f"[ERROR] Al escribir {report_23_path}: {e}")

# 6. Guardar Transacciones Acumuladas con Formato Corporativo (#1F4E78)
try:
    from data.exporter import guardar_transacciones_acumuladas_excel
    success = guardar_transacciones_acumuladas_excel(df_raw, raw_path)
    if success:
        print(f"[EXITO] {raw_path} guardado y actualizado con formato corporativo Azul Oscuro (#1F4E78).")
    else:
        print(f"[ADVERTENCIA] No se pudo escribir {raw_path} (Asegúrese de cerrar Excel si está abierto).")
except PermissionError:
    print(f"[ADVERTENCIA] No se pudo escribir {raw_path} porque está abierto en Excel. Por favor ciérrelo.")
except Exception as e:
    print(f"[ERROR] Al escribir {raw_path}: {e}")

# 7. Sincronizar Base de Datos SQLite
sincronizar_aprobaciones_desde_asistencia()
print("[EXITO] Base de datos SQLite y panel de aprobaciones sincronizados.")
