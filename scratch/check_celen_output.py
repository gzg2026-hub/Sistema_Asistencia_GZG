import openpyxl

report_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\Reporte_Asistencia_GZG_2026-08-17_002739.xlsx"
wb = openpyxl.load_workbook(report_path)
ws = wb.active

print("=== VERIFICACIÓN CELEN RUIZ EN NUEVO REPORTE ===")
for row in ws.iter_rows(min_row=5, values_only=True):
    apellidos = str(row[1]).strip() if row[1] is not None else ""
    if "CELEN" in apellidos:
        vals = [cell for cell in row]
        print(f"Fecha: {vals[5]} | Turno: {vals[7]} | Ent: {vals[8]} {vals[9]} | Sal: {vals[10]} {vals[11]} | Trab (HH:MM): {vals[16]} | Obs: {vals[21]}")
