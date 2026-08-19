import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\hikvision\Transacciones_2026-08-18_2026-08-18_091000.xlsx")
ws = wb.active

rows = list(ws.iter_rows(values_only=True))
print("RECORDS FOR RAUL ESPINOZA:")
for r in rows:
    if r[0] == "44955960" or "ESPINOZA" in str(r[2]):
        print("  ", r)
