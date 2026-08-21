import os
import openpyxl

report_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\Reporte_Asistencia_GZG_2026-08-17_v2.xlsx"
wb = openpyxl.load_workbook(report_path)
ws = wb.active

print(f"=== VERIFICACIÓN EN {os.path.basename(report_path)} ===")

def print_worker(dni_search, title):
    print(f"\n--- {title} ({dni_search}) ---")
    found = False
    for row in ws.iter_rows(min_row=5, values_only=False):
        dni_val = str(row[0].value).strip() if row[0].value else ""
        if dni_search in dni_val:
            found = True
            vals = [cell.value for cell in row]
            fill = row[20].fill.start_color.rgb if row[20].fill and row[20].fill.start_color else "Sin Relleno"
            print(f"Fecha: {vals[5]} | Turno: {vals[7]} | Ent: {vals[8]} {vals[9]} | Sal: {vals[10]} {vals[11]} | Trab: {vals[16]} | Exc: {vals[18]} | HE: {vals[19]} | Tipo: {vals[20]} | Obs: {vals[21]} | Color: {fill}")
    if not found:
        print("No encontrado.")

print_worker("47783594", "1. Jhon Robert Agreda Aspajo")
print_worker("03208053", "5. Franco Moreto Bermeo")
print_worker("6616501", "6. Yenkli Ordoñez Arteaga")
print_worker("41219221", "7. Jose Ismael Vigo Rafael")
print_worker("46181231", "8. Jose Orlando Moncada Rejas")
