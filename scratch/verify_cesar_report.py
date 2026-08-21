import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\downloads\data_procesada\Reporte_Asistencia_GZG_2026-08-18.xlsx")
ws = wb.active

rows = list(ws.iter_rows(values_only=True))
print("PROCESSED ATTENDANCE REPORT FOR CESAR RIMARACHIN:")
for r in rows:
    if r[0] == "77386038" or "RIMARACHIN" in str(r[1]):
        print("  DNI:", r[0])
        print("  Trabajador:", r[1], r[2])
        print("  Fecha Turno:", r[5])
        print("  Turno:", r[7])
        print("  Fecha Entrada:", r[8], "Hora Entrada:", r[9])
        print("  Fecha Salida:", r[10], "Hora Salida:", r[11])
        print("  Horas Trabajadas:", r[16])
        print("  Estado:", r[20])
