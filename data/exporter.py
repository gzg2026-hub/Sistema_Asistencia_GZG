"""
exporter.py
===========
Genera el reporte consolidado de asistencia en un ÚNICO Excel de una sola pestaña
("Asistencia y Horas Extras") con el formato ejecutivo proporcionado (alturas de fila holgadas,
anchos de columna legibles y proporcionales, encabezados azul marino y formato texto en DNI).
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
    """Convierte cualquier representación de fecha a formato latino DD-MM-YYYY (ej. 01-08-2026)."""
    if pd.isna(date_val) or date_val is None or date_val == "":
        return ""
    val_str = str(date_val).strip().split(' ')[0]
    try:
        if '-' in val_str:
            parts = val_str.split('-')
            if len(parts[0]) == 4:  # YYYY-MM-DD -> DD-MM-YYYY
                return f"{parts[2]:0>2}-{parts[1]:0>2}-{parts[0]}"
            elif len(parts[2]) == 4:  # DD-MM-YYYY
                return f"{parts[0]:0>2}-{parts[1]:0>2}-{parts[2]}"
        elif '/' in val_str:
            parts = val_str.split('/')
            if len(parts[2]) == 4:  # DD/MM/YYYY
                return f"{parts[0]:0>2}-{parts[1]:0>2}-{parts[2]}"
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
    con proporciones holgadas de filas y columnas ejecutivas.
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

    # Banner Título (Fila 1)
    ws.row_dimensions[1].height = 28
    ws.merge_cells("A1:S1")
    ws["A1"] = "REPORTE DE ASISTENCIA Y HORAS EXTRAS PROCESADO (TURNOS DÍA Y NOCHE)"
    ws["A1"].fill = fill_banner_title
    ws["A1"].font = font_banner_title
    ws["A1"].alignment = align_center

    # Banner Subtítulo (Fila 2)
    ws.row_dimensions[2].height = 20
    ws.merge_cells("A2:S2")
    ws["A2"] = f"GZG Minerales | Período: {f_min} a {f_max} | Incluye Entrada, Salida, Exceso de Jornada y Horas Extras"
    ws["A2"].fill = fill_banner_sub
    ws["A2"].font = font_banner_sub
    ws["A2"].alignment = align_center

    ws.row_dimensions[3].height = 10
    ws.append([])  # Fila 3 vacía de separación

    # Encabezados de Columna (Fila 4)
    ws.row_dimensions[4].height = 28
    headers = [
        "DNI", "Apellidos", "Nombres", "Departamento", "Posición",
        "Fecha Turno", "Día", "Turno", "Fecha Entrada", "Hora Entrada",
        "Fecha Salida", "Hora Salida", "Horas Trabajadas (HH:MM)",
        "Tardanza (HH:MM)", "Exceso Jornada (HH:MM)", "Horas Extras (HH:MM)",
        "Método Verificación", "Tipo Registro", "Observación / Incidencias"
    ]

    ws.append(headers)  # Fila 4

    for cell in ws[4]:
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = align_center

    # Mapeo rápido de métodos de verificación por marcación si existe df_marcaciones
    metodos_map = {}
    if df_marcaciones is not None and not df_marcaciones.empty:
        dni_c = 'ID' if 'ID' in df_marcaciones.columns else 'DNI'
        fecha_c = 'Fecha' if 'Fecha' in df_marcaciones.columns else 'FECHA'
        met_c = 'Método de verificación' if 'Método de verificación' in df_marcaciones.columns else 'METODO'
        if dni_c in df_marcaciones.columns and fecha_c in df_marcaciones.columns and met_c in df_marcaciones.columns:
            for _, m_row in df_marcaciones.iterrows():
                k = (str(m_row[dni_c]).strip(), str(m_row[fecha_c]).strip())
                val_met = str(m_row[met_c]).strip()
                if val_met and val_met != '--':
                    metodos_map[k] = val_met

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

            f_ent = fecha_t if h_ent else ""
            f_sal = fecha_t if h_sal else ""

            h_trab = format_hhmm_cell(row.get('HORAS TRABAJADAS (HH:MM)', row.get('HORAS TRABAJADAS', '00:00')), is_hours_float=True)
            tard = format_hhmm_cell(row.get('TARDANZA (HH:MM)', row.get('TARDANZA (MIN)', '00:00')), is_hours_float=False)
            exc = format_hhmm_cell(row.get('EXCESO JORNADA (HH:MM)', row.get('EXCESO JORNADA', '00:00')), is_hours_float=False)
            he = format_hhmm_cell(row.get('TOTAL HORAS ADICIONALES (HH:MM)', row.get('TOTAL HORAS ADICIONALES', '00:00')), is_hours_float=False)

            metodo = metodos_map.get((dni, fecha_t), "Huella dactilar")
            incid = str(row.get('INCIDENCIAS', '')).strip()

            tipo_reg = "Normal"
            if "duplicad" in incid.lower():
                tipo_reg = "Duplicado (Entrada)" if "entrada" in incid.lower() else "Duplicado (Salida)"
            elif "sin registro de entrada" in incid.lower():
                tipo_reg = "Salida sin entrada"

            ws.append([
                dni, apellidos, nombres, dept, posicion,
                fecha_t, dia_str, turno, f_ent, h_ent,
                f_sal, h_sal, h_trab, tard, exc, he,
                metodo, tipo_reg, incid
            ])

            # Aplicar bordes, fuente y alineaciones a la nueva fila
            current_row = ws.max_row
            ws.row_dimensions[current_row].height = 20
            for c_idx in range(1, 20):
                cell = ws.cell(row=current_row, column=c_idx)
                cell.font = font_data
                cell.border = thin_border
                cell.alignment = align_center if c_idx not in (2, 3, 4, 5, 19) else align_left
                
                # Formato de celda DNI como Texto '@'
                if c_idx == 1:
                    cell.number_format = '@'

    # Anchos de columna holgados y proporcionales
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
        13: 25,  # Horas Trabajadas (HH:MM)
        14: 18,  # Tardanza (HH:MM)
        15: 22,  # Exceso Jornada (HH:MM)
        16: 20,  # Horas Extras (HH:MM)
        17: 22,  # Método Verificación
        18: 22,  # Tipo Registro
        19: 48   # Observación / Incidencias
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
    """Guarda directamente el reporte procesado de una sola hoja en la carpeta raíz del proyecto."""
    excel_bytes = exportar_asistencia_excel(
        df_trabajadores, df_marcaciones, df_asistencia, df_horas_extra, df_incidencias, target_path
    )
    try:
        with open(target_path, "wb") as f:
            f.write(excel_bytes)
        return True
    except PermissionError:
        ts = datetime.now().strftime("%H%M%S")
        alt_path = target_path.replace(".xlsx", f"_{ts}.xlsx")
        try:
            with open(alt_path, "wb") as f:
                f.write(excel_bytes)
            print(f"[Warn] Archivo en uso. Guardado como: '{alt_path}'")
            return True
        except Exception:
            return False
    except Exception as e:
        print(f"[Error] Error al guardar Excel base: {e}")
        return False
