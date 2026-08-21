import openpyxl

raw_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_2026-08-17_2026-08-21.xlsx"
proc_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\Reporte_Asistencia_GZG_2026-08-17_al_2026-08-21.xlsx"

wb_raw = openpyxl.load_workbook(raw_path)
ws_raw = wb_raw.active
raw_headers = [cell for cell in ws_raw[1]]

print("=== VERIFICACIÓN DATA CRUDA ===")
print(f"Archivo: {raw_path}")
print(f"Total Marcaciones Raw: {ws_raw.max_row - 1}")
print("Encabezados Fila 1 Raw:")
print([c.value for c in raw_headers[:5]])

wb_proc = openpyxl.load_workbook(proc_path)
ws_proc = wb_proc.active
proc_headers = [cell for cell in ws_proc[4]]

print("\n=== VERIFICACIÓN DATA PROCESADA ===")
print(f"Archivo: {proc_path}")
print(f"Total Filas de Asistencia: {ws_proc.max_row - 4}")
print("Encabezados Fila 4 Procesado (16 a 20):")
print([c.value for c in proc_headers[16:20]])
