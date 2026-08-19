import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Sistema_Asistencia_GZG_v1.0.xlsx", data_only=True)
ws = wb.active

print("--- REGISTRO DE ESPINOZA SAAVEDRA RAUL ESTEBAN EN MASTER EXCEL ---")
for row in ws.iter_rows(values_only=True):
    row_str = [str(c or '') for c in row]
    if '44955960' in row_str or 'ESPINOZA SAAVEDRA' in row_str:
        print("Fila:", row_str)
