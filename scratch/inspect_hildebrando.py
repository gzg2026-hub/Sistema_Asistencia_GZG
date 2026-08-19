import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Reporte_Asistencia_Procesado_Nuevo.xlsx", data_only=True)
ws = wb.active

print("--- REGISTRO DE HILDEBRANDO RAMIREZ LABÁN ---")
for row in ws.iter_rows(values_only=True):
    row_str = [str(c or '') for c in row]
    if '71060137' in row_str or 'HILDEBRANDO' in row_str or 'RAMIREZ LABÁN' in row_str:
        print("Fila:", row_str)
