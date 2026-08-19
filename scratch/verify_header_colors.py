import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\hikvision\Transacciones_2026-08-17_2026-08-17_162521.xlsx")
ws = wb.active

for cell in ws[1]:
    fill_color = cell.fill.start_color.rgb if cell.fill else "None"
    font_color = cell.font.color.rgb if cell.font and cell.font.color else "None"
    print(f"Cell {cell.coordinate}: Header='{cell.value}' | Fill={fill_color} | FontColor={font_color} | Bold={cell.font.bold}")
