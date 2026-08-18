import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\hikvision\Transacciones_2026-08-17_2026-08-17_132711.xlsx", data_only=True)
ws = wb.active

for idx, row in enumerate(ws.iter_rows(values_only=True)):
    if idx < 15:
        print([str(c) for c in row])
