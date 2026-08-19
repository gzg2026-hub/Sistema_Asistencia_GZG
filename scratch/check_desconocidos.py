import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Sistema_Asistencia_GZG_v1.0.xlsx", data_only=True)
ws = wb.active

desc_count = 0
for row in ws.iter_rows(values_only=True):
    row_str = [str(c or '') for c in row]
    if 'DESCONOCIDO' in row_str:
        desc_count += 1
        print("DESCONOCIDO encontrado:", row_str[:12])

print(f"Total filas DESCONOCIDO restantes en Excel: {desc_count}")
