"""
exporter.py
===========
Genera el reporte consolidado de asistencia en un ÚNICO Excel de una sola pestaña
("Asistencia y Horas Extras") con el formato ejecutivo oficial limpio de 23 columnas
(sin ninguna columna de punto de control).
"""

import io
import os
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Optional, Dict

BASE_EXCEL_TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Sistema_Asistencia_GZG_v1.0.xlsx")

DIAS_SEMANA = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}


def format_date_ddmmyyyy(date_val) -> str:
    """Convierte cualquier representación de fecha a formato DD/MM/YYYY (ej. 18/08/2026)."""
    if pd.isna(date_val) or date_val is None or date_val == "" or str(date_val).strip() == "-":
        return "-" if str(date_val).strip() == "-" else ""
    val_str = str(date_val).strip().split(' ')[0]
    try:
        if '-' in val_str:
            parts = val_str.split('-')
            if len(parts[0]) == 4:  # YYYY-MM-DD -> DD/MM/YYYY
                return f"{int(parts[2]):02d}/{int(parts[1]):02d}/{parts[0]}"
            elif len(parts[2]) == 4:  # DD-MM-YYYY
                return f"{int(parts[0]):02d}/{int(parts[1]):02d}/{parts[2]}"
        elif '/' in val_str:
            parts = val_str.split('/')
            if len(parts[2]) == 4:  # DD/MM/YYYY
                return f"{int(parts[0]):02d}/{int(parts[1]):02d}/{parts[2]}"
    except Exception:
        pass
    return val_str


def format_hhmm_cell(val, is_hours_float=False) -> str:
    """Convierte minutos enteros u horas flotantes a string HH:MM (ej. 11:51, 00:15)."""
    if pd.isna(val) or val is None or val == "":
        return "00:00"
    val_str = str(val).strip()
    if ":" in val_str and len(val_str.split(":")) == 2:
        return val_str
    try:
        num = float(val)
        if num <= 0:
            return "00:00"
        total_min = int(round(num * 60.0)) if is_hours_float else int(round(num))
        h = total_min // 60
        m = total_min % 60
        return f"{h:02d}:{m:02d}"
    except Exception:
        return "00:00"

# ... (resto de funciones)



@st.cache_data(ttl=60, show_spinner=False)
def exportar_asistencia_excel(
    df_trabajadores: pd.DataFrame,
    df_marcaciones: pd.DataFrame,
    df_asistencia: pd.DataFrame,
    df_horas_extra: pd.DataFrame = None,
    df_incidencias: pd.DataFrame = None,
    template_path: str = BASE_EXCEL_TEMPLATE
) -> bytes:
    """
    Genera el archivo Excel procesado oficial de UNA SOLA HOJA ('Asistencia y Horas Extras')
    con 23 columnas limpias (sin ninguna columna de punto de control).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Asistencia y Horas Extras"
    ws.views.sheetView[0].showGridLines = True

    # 1. Rango de Fechas para el banner
    f_min = "2026-08-17"
    f_max = "2026-08-18"
    if df_asistencia is not None and not df_asistencia.empty and 'FECHA' in df_asistencia.columns:
        fechas_val = df_asistencia['FECHA'].dropna().unique()
        if len(fechas_val) > 0:
            f_min = str(min(fechas_val))
            f_max = str(max(fechas_val))

    # Estilos profesionales openpyxl
    fill_banner_title = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    font_banner_title = Font(name="Calibri", size=13, bold=True, color="FFFFFF")

    fill_banner_sub = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    font_banner_sub = Font(name="Calibri", size=10, italic=True, bold=True, color="1F4E78")

    fill_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

    font_data = Font(name="Calibri", size=10)

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # Banner Título (Fila 1 - 23 columnas A a W)
    ws.row_dimensions[1].height = 28
    ws.merge_cells("A1:W1")
    ws["A1"] = "REPORTE DE ASISTENCIA Y HORAS EXTRAS PROCESADO (TURNOS DÍA Y NOCHE)"
    ws["A1"].fill = fill_banner_title
    ws["A1"].font = font_banner_title
    ws["A1"].alignment = align_center

    # Banner Subtítulo (Fila 2)
    ws.row_dimensions[2].height = 20
    ws.merge_cells("A2:V2")
    ws["A2"] = f"GZG Minerales | Período: {f_min} a {f_max} | Incluye Entrada, Salida, Inicio H.E. y Fin H.E."
    ws["A2"].fill = fill_banner_sub
    ws["A2"].font = font_banner_sub
    ws["A2"].alignment = align_center

    ws.row_dimensions[3].height = 10
    ws.append([])  # Fila 3 vacía de separación

    # Encabezados de Columna (Fila 4 - 22 columnas)
    ws.row_dimensions[4].height = 28
    headers = [
        "DNI", "Apellidos", "Nombres", "Departamento", "Posición",
        "Fecha Turno", "Día", "Turno", "Fecha Entrada", "Hora Entrada",
        "Fecha Salida", "Hora Salida",
        "Fecha Inicio H.E.", "Hora Inicio H.E.",
        "Fecha Fin H.E.", "Hora Fin H.E.",
        "Horas Trabajadas (hh:mm)", "Tardanza (hh:mm)", "Exceso Jornada (hh:mm)", "Horas Extras Totales (hh:mm)",
        "Tipo Registro", "Observación / Incidencias"
    ]

    ws.append(headers)  # Fila 4

    for cell in ws[4]:
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = align_center

    # Escribir filas procesadas
    if df_asistencia is not None and not df_asistencia.empty:
        for _, row in df_asistencia.iterrows():
            dni = str(row.get('DNI', '')).strip()
            apellidos = str(row.get('APELLIDOS', '')).strip()
            nombres = str(row.get('NOMBRES', '')).strip()
            dept = str(row.get('ÁREA', row.get('Departamento', ''))).strip()
            posicion = str(row.get('CARGO', row.get('Posición', ''))).strip()
            fecha_t = str(row.get('FECHA', '')).strip()

            # Día de la semana
            dia_str = ""
            try:
                dt_obj = datetime.strptime(fecha_t, "%Y-%m-%d")
                dia_str = DIAS_SEMANA.get(dt_obj.weekday(), "")
            except Exception:
                dia_str = ""

            turno = str(row.get('TURNO', 'DIA')).strip()
            h_ent = str(row.get('ENTRADA', '')).strip() if pd.notna(row.get('ENTRADA')) else ""
            h_sal = str(row.get('SALIDA', '')).strip() if pd.notna(row.get('SALIDA')) else ""

            f_ent = str(row.get('FECHA_ENTRADA', fecha_t if h_ent else '')).strip()
            f_sal = str(row.get('FECHA_SALIDA', fecha_t if h_sal else '')).strip()

            # Regla Punto 9: Eliminar filas cuando la doble columna I (Fecha Entrada) y K (Fecha Salida) sean NAN o vacías
            if (not f_ent or f_ent.lower() in ('nan', 'none', '', '-')) and (not f_sal or f_sal.lower() in ('nan', 'none', '', '-')) and not h_ent and not h_sal:
                continue

            # Marcaciones H.E.
            f_ini_he = str(row.get('FECHA_INICIO_HE', '-')).strip()
            h_ini_he = str(row.get('HORA_INICIO_HE', '-')).strip()
            f_fin_he = str(row.get('FECHA_FIN_HE', '-')).strip()
            h_fin_he = str(row.get('HORA_FIN_HE', '-')).strip()

            # Función flexible para extraer valores por nombres aproximados de columna (Punto 2)
            def get_row_val(row_obj, *keys):
                for k in keys:
                    if k in row_obj and pd.notna(row_obj[k]):
                        return row_obj[k]
                return '00:00'

            val_trab = get_row_val(row, 'HORAS TRABAJADAS (hh:mm)', 'HORAS TRABAJADAS (HH:MM)', 'HORAS TRABAJADAS')
            val_tard = get_row_val(row, 'TARDANZA (hh:mm)', 'TARDANZA (HH:MM)', 'TARDANZA (MIN)')
            val_exc = get_row_val(row, 'EXCESO JORNADA (hh:mm)', 'EXCESO JORNADA (HH:MM)', 'EXCESO JORNADA')
            val_he = get_row_val(row, 'HORAS EXTRAS TOTALES (hh:mm)', 'TOTAL HORAS ADICIONALES (hh:mm)', 'TOTAL HORAS ADICIONALES', 'HORAS EXTRAS (HH:MM)')

            h_trab = format_hhmm_cell(val_trab, is_hours_float=True)
            tard = format_hhmm_cell(val_tard, is_hours_float=False)
            exc = format_hhmm_cell(val_exc, is_hours_float=False)
            he = format_hhmm_cell(val_he, is_hours_float=False)

            fecha_t_formatted = format_date_ddmmyyyy(fecha_t)
            f_ent_formatted = format_date_ddmmyyyy(f_ent)
            f_sal_formatted = format_date_ddmmyyyy(f_sal)
            f_ini_he_formatted = format_date_ddmmyyyy(f_ini_he)
            f_fin_he_formatted = format_date_ddmmyyyy(f_fin_he)

            incid = str(row.get('INCIDENCIAS', '')).strip()
            tipo_reg = str(row.get('TIPO_REGISTRO', 'Normal')).strip()

            ws.append([
                dni, apellidos, nombres, dept, posicion,
                fecha_t_formatted, dia_str, turno, f_ent_formatted, h_ent,
                f_sal_formatted, h_sal,
                f_ini_he_formatted, h_ini_he,
                f_fin_he_formatted, h_fin_he,
                h_trab, tard, exc, he,
                tipo_reg, incid
            ])

            # Colores pastel de sombreado
            fill_jornada_parcial = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") # Amarillo Pastel
            fill_cambio_turno = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")    # Azul Pastel
            fill_incidencia = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")      # Durazno Pastel

            # Aplicar bordes, fuente, alineaciones y sombreado a la nueva fila
            current_row = ws.max_row
            ws.row_dimensions[current_row].height = 20
            for c_idx in range(1, 23):
                cell = ws.cell(row=current_row, column=c_idx)
                cell.font = font_data
                cell.border = thin_border
                cell.alignment = align_center if c_idx not in (2, 3, 4, 5, 22) else align_left
                
                # Resaltado con colores pastel según tipo de registro u observación (Punto 10: Cambio de guardia, relevo o media jornada usan el mismo color pastel)
                comb_check = (tipo_reg + " " + incid).lower()
                if "jornada parcial" in comb_check or "medio día" in comb_check or "media jornada" in comb_check or "cambio de guardia" in comb_check or "relevo" in comb_check:
                    cell.fill = fill_cambio_turno
                elif "pendiente" in comb_check or "falta" in comb_check or "sin registro" in comb_check:
                    cell.fill = fill_incidencia

                # Formato de celda DNI como Texto '@'
                if c_idx == 1:
                    cell.number_format = '@'

    # Anchos de columna holgados y proporcionales (22 columnas)
    PROPORTIONAL_WIDTHS = {
        1: 15,   # DNI
        2: 26,   # Apellidos
        3: 24,   # Nombres
        4: 28,   # Departamento
        5: 24,   # Posición
        6: 15,   # Fecha Turno
        7: 13,   # Día
        8: 12,   # Turno
        9: 15,   # Fecha Entrada
        10: 14,  # Hora Entrada
        11: 15,  # Fecha Salida
        12: 14,  # Hora Salida
        13: 16,  # Fecha Inicio H.E.
        14: 15,  # Hora Inicio H.E.
        15: 16,  # Fecha Fin H.E.
        16: 15,  # Hora Fin H.E.
        17: 25,  # Horas Trabajadas (HH:MM)
        18: 18,  # Tardanza (HH:MM)
        19: 22,  # Exceso Jornada (HH:MM)
        20: 20,  # Horas Extras (HH:MM)
        21: 22,  # Tipo Registro
        22: 48   # Observación / Incidencias
    }

    for col_idx, width in PROPORTIONAL_WIDTHS.items():
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def guardar_excel_base(
    df_trabajadores: pd.DataFrame,
    df_marcaciones: pd.DataFrame,
    df_asistencia: pd.DataFrame,
    df_horas_extra: pd.DataFrame = None,
    df_incidencias: pd.DataFrame = None,
    target_path: str = BASE_EXCEL_TEMPLATE
) -> bool:
    """Guarda el reporte procesado en la raíz y en downloads/data_procesada."""
    excel_bytes = exportar_asistencia_excel(
        df_trabajadores, df_marcaciones, df_asistencia, df_horas_extra, df_incidencias, target_path
    )
    
    # 1. Guardar en carpeta raíz
    success = False
    try:
        with open(target_path, "wb") as f:
            f.write(excel_bytes)
        success = True
    except PermissionError:
        ts = datetime.now().strftime("%H%M%S")
        alt_path = target_path.replace(".xlsx", f"_{ts}.xlsx")
        try:
            with open(alt_path, "wb") as f:
                f.write(excel_bytes)
            print(f"[Warn] Archivo en uso. Guardado como: '{alt_path}'")
            success = True
        except Exception:
            pass
    except Exception as e:
        print(f"[Error] Error al guardar Excel base: {e}")

    # 2. Guardar copia en downloads/data_procesada/
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        carpeta_proc = os.path.join(project_root, "downloads", "data_procesada")
        os.makedirs(carpeta_proc, exist_ok=True)
        
        fecha_str = datetime.now().strftime("%Y-%m-%d")
        if not df_asistencia.empty and "FECHA_ENTRADA" in df_asistencia.columns:
            fechas = df_asistencia["FECHA_ENTRADA"].dropna().unique()
            if len(fechas) > 0:
                fecha_str = str(fechas[0])
                
        proc_filename = f"Reporte_Asistencia_GZG_{fecha_str}.xlsx"
        proc_path = os.path.join(carpeta_proc, proc_filename)
        
        try:
            with open(proc_path, "wb") as f:
                f.write(excel_bytes)
        except PermissionError:
            ts = datetime.now().strftime("%H%M%S")
            proc_path_ts = os.path.join(carpeta_proc, f"Reporte_Asistencia_GZG_{fecha_str}_{ts}.xlsx")
            with open(proc_path_ts, "wb") as f:
                f.write(excel_bytes)
    except Exception as e:
        print(f"[Warn] No se pudo guardar copia en data_procesada: {e}")

    return success
