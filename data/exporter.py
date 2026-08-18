import io
import os
import openpyxl
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Optional, Dict

BASE_EXCEL_TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Sistema_Asistencia_GZG_v1.0.xlsx")

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
    df_horas_extra: pd.DataFrame,
    df_incidencias: pd.DataFrame,
    template_path: str = BASE_EXCEL_TEMPLATE
) -> bytes:
    """Genera un archivo Excel limpio y ultra-rápido en memoria RAM con las 5 pestañas oficiales."""
    output = io.BytesIO()
    
    OFFICIAL_SCHEMAS = {
        '01_TRABAJADORES': ['DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'AREA'],
        '02_MARCACIONES': [
            'FECHA', 'ID', 'Nombre', 'Apellido', 'Cargo', 'Departamento',
            'Grupo de asistencia', 'Tiempo', 'Tipo de pase de tarjeta',
            'Método de verificación', 'Punto de control de asistencia'
        ],
        '03_ASISTENCIA': [
            'FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'ÁREA', 'TURNO',
            'ENTRADA', 'SALIDA', 'HORAS TRABAJADAS (HH:MM)',
            'TARDANZA (HH:MM)', 'SALIDA ANTICIPADA (HH:MM)', 'EXCESO JORNADA (HH:MM)',
            'TOTAL HORAS ADICIONALES (HH:MM)', 'INCIDENCIAS', 'ESTADO ASISTENCIA', 'OBSERVACIONES'
        ],
        '04_HORAS_EXTRA': [
            'FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'ÁREA', 'TURNO', 'INICIO H.E.', 'FIN H.E.', 'DURACIÓN (HH:MM)', 'OBSERVACIÓN'
        ],
        '05_INCIDENCIAS': [
            'FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'ÁREA', 'TIPO', 'HORA', 'DESCRIPCIÓN', 'SEVERIDAD', 'OBSERVACIÓN'
        ]
    }

    target_sheets = [
        ('01_TRABAJADORES', df_trabajadores),
        ('02_MARCACIONES', df_marcaciones),
        ('03_ASISTENCIA', df_asistencia),
        ('04_HORAS_EXTRA', df_horas_extra),
        ('05_INCIDENCIAS', df_incidencias)
    ]
    
    from openpyxl.styles import PatternFill, Font, Alignment

    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df_raw in target_sheets:
            official_headers = OFFICIAL_SCHEMAS.get(sheet_name, [])
            if df_raw is not None and not df_raw.empty:
                df_clean = df_raw.copy()
                valid_cols = [c for c in official_headers if c in df_clean.columns]
                if valid_cols:
                    df_clean = df_clean[valid_cols]
                df_clean.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                pd.DataFrame(columns=official_headers).to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Dar formato azul pastel a los encabezados del libro de trabajo
            ws = writer.sheets[sheet_name]
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_align
            
            # Autoajustar ancho de columnas
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    return output.getvalue()

def guardar_excel_base(
    df_trabajadores: pd.DataFrame,
    df_marcaciones: pd.DataFrame,
    df_asistencia: pd.DataFrame,
    df_horas_extra: pd.DataFrame,
    df_incidencias: pd.DataFrame,
    target_path: str = BASE_EXCEL_TEMPLATE
) -> bool:
    """Guarda directamente los resultados en el archivo Excel base de forma totalmente segura sin corromper la estructura."""
    excel_bytes = exportar_asistencia_excel(
        df_trabajadores, df_marcaciones, df_asistencia, df_horas_extra, df_incidencias, target_path
    )
    try:
        if os.path.exists(target_path) and target_path.lower().endswith('.xlsm'):
            is_xlsm = True
            wb = openpyxl.load_workbook(target_path, keep_vba=True)
            target_sheets = [
                ('01_TRABAJADORES', df_trabajadores, ['DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'AREA']),
                ('02_MARCACIONES', df_marcaciones, [
                    'FECHA', 'ID', 'Nombre', 'Apellido', 'Cargo', 'Departamento',
                    'Grupo de asistencia', 'Tiempo', 'Tipo de pase de tarjeta',
                    'Método de verificación', 'Punto de control de asistencia'
                ]),
                ('03_ASISTENCIA', df_asistencia, [
                    'FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'ÁREA', 'TURNO',
                    'ENTRADA', 'SALIDA', 'HORAS TRABAJADAS (HH:MM)',
                    'TARDANZA (HH:MM)', 'SALIDA ANTICIPADA (HH:MM)', 'EXCESO JORNADA (HH:MM)',
                    'TOTAL HORAS ADICIONALES (HH:MM)', 'INCIDENCIAS', 'ESTADO ASISTENCIA', 'OBSERVACIONES'
                ]),
                ('04_HORAS_EXTRA', df_horas_extra, [
                    'FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'ÁREA', 'TURNO', 'INICIO H.E.', 'FIN H.E.', 'DURACIÓN (HH:MM)', 'OBSERVACIÓN'
                ]),
                ('05_INCIDENCIAS', df_incidencias, [
                    'FECHA', 'DNI', 'APELLIDOS', 'NOMBRES', 'CARGO', 'ÁREA', 'TIPO', 'HORA', 'DESCRIPCIÓN', 'SEVERIDAD', 'OBSERVACIÓN'
                ])
            ]
            for s_name, df_data, headers in target_sheets:
                if s_name in wb.sheetnames:
                    ws = wb[s_name]
                    ws.delete_rows(1, ws.max_row + 1)
                else:
                    ws = wb.create_sheet(title=s_name)

                ws.append(headers)
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = header_align

                if df_data is not None and not df_data.empty:
                    valid_cols = [c for c in headers if c in df_data.columns]
                    df_sub = df_data[valid_cols]
                    for row in df_sub.itertuples(index=False, name=None):
                        ws.append([str(v) if v is not None else '' for v in row])

            wb.save(target_path)
            wb.close()
            return True

        with open(target_path, "wb") as f:
            f.write(excel_bytes)
        return True
    except PermissionError:
        print(f"[Warn] No se pudo sobrescribir '{target_path}' porque el archivo está abierto en Microsoft Excel.")
        return False
    except Exception as e:
        print(f"[Error] Error al guardar Excel base: {e}")
        return False
