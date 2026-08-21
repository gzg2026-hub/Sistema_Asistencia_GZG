import openpyxl

file_path = r"C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_cruda\Transacciones_2026-08-18_2026-08-19.xlsx"
wb = openpyxl.load_workbook(file_path)
ws = wb.active

rows = list(ws.iter_rows(values_only=True))
print("TOTAL ROWS IN DOWNLOADED EXCEL:", len(rows))
if rows:
    print("HEADER:", rows[0])
    if len(rows) > 1:
        print("FIRST ROW:", rows[1])
