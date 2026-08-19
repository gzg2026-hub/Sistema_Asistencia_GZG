import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\hikvision\Transacciones_2026-08-18_2026-08-18_085536.xlsx")
ws = wb.active

rows = list(ws.iter_rows(values_only=True))
print(f"Total filas en Excel guardado: {len(rows)}")
print("Encabezados:", rows[0])
print("Primeras 3 filas de datos:")
for r in rows[1:4]:
    print(" ", r)
