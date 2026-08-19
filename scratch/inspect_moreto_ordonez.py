import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Sistema_Asistencia_GZG_v1.0.xlsx", data_only=True)
ws = wb.active

print("--- REGISTROS DE MORETO BERMEO Y ORDOÑEZ ARTEAGA EN MASTER EXCEL ---")
for row in ws.iter_rows(values_only=True):
    row_str = [str(c or '') for c in row]
    if any(k in row_str for k in ['03208053', '3208053', '006616501', '6616501', 'MORETO BERMEO', 'ORDOÑEZ ARTEAGA', 'ORDO\ufffdEZ ARTEAGA']):
        print("Fila:", row_str[:12])
