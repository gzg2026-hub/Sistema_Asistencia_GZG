import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Reporte_Asistencia_Procesado.xlsx", data_only=True)
ws = wb.active

print("--- PRIMERAS 15 FILAS DE ASISTENCIA ---")
for idx, row in enumerate(ws.iter_rows(values_only=True)):
    if 4 <= idx <= 18:
        print(f"Fila {idx}:", [str(c or '') for c in row[8:21]])
