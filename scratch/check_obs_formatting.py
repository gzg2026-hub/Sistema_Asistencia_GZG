import os
import openpyxl

report_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\Reporte_Asistencia_GZG_2026-08-17_001730.xlsx"
wb = openpyxl.load_workbook(report_path)
ws = wb.active

print(f"=== VERIFICACIÓN DE OBSERVACIONES EN {os.path.basename(report_path)} ===")

obs_list = []
for row in ws.iter_rows(min_row=5, values_only=True):
    obs = str(row[21]).strip() if row[21] is not None else ""
    if obs and obs != "None":
        obs_list.append(f"{row[1]} {row[2]} ({row[5]}): {obs}")

for sample in obs_list[:25]:
    print(sample)
