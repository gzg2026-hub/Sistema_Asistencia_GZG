import openpyxl

report_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Reporte_Asistencia_GZG_2026-08-17_al_2026-08-21.xlsx"
wb = openpyxl.load_workbook(report_path)
ws = wb.active

print(f"=== VERIFICACION DE CAMBIO COLUMNA U Y COLUMNA V EN {report_path} ===")

count = 0
for row in ws.iter_rows(min_row=5, values_only=True):
    col_u = str(row[20])
    col_v = str(row[21])
    if "Jornada parcial" in col_v:
        count += 1
        print(f"  * {row[1]} {row[2]} ({row[5]}): Col U (Tipo): '{col_u}' | Col V (Obs): '{col_v}'")

print(f"\nTotal filas de media jornada verificadas: {count}")
