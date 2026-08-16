import io
import os
import openpyxl
from openpyxl.utils import get_column_letter
import pandas as pd
from datetime import datetime
from typing import Optional, Dict

BASE_EXCEL_TEMPLATE = r"C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Sistema_Asistencia_GZG_v1.0.xlsm"

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

def exportar_asistencia_excel(
    df_trabajadores: pd.DataFrame,
    df_marcaciones: pd.DataFrame,
    df_asistencia: pd.DataFrame,
    df_horas_extra: pd.DataFrame,
    df_incidencias: pd.DataFrame,
    template_path: str = BASE_EXCEL_TEMPLATE
) -> bytes:
    """
    Genera un archivo Excel totalmente limpio con exactamente las 5 pestañas oficiales
    y ajusta automáticamente el ancho de las columnas.
    """
    wb = openpyxl.Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)
    
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
    
    for sheet_name, df in target_sheets:
        ws = wb.create_sheet(title=sheet_name)
        official_headers = OFFICIAL_SCHEMAS.get(sheet_name, list(df.columns) if df is not None else [])
        
        # Escribir encabezados oficiales
        ws.append(official_headers)
        
        # Formato de celda de encabezado
        for col_idx in range(1, len(official_headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
            cell.fill = openpyxl.styles.PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
            cell.alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")
            
        if df is not None and not df.empty:
            current_cols = list(df.columns)
            col_map = {}
            for target_col in official_headers:
                t_clean = target_col.lower().replace('á', 'a').replace('ó', 'o').replace('é', 'e').replace(' (min)', '').replace(' (hh:mm)', '').strip()
                for c in current_cols:
                    c_clean = c.lower().replace('á', 'a').replace('ó', 'o').replace('é', 'e').replace(' (min)', '').replace(' (hh:mm)', '').strip()
                    if c_clean == t_clean:
                        col_map[target_col] = c
                        break
                        
            for r_idx, row in df.iterrows():
                # Omitir filas basura o desalineadas
                dni_val = str(row.get('DNI', row.get('ID', ''))).strip().lower()
                if 'fecha:' in dni_val or 'semana:' in dni_val or dni_val == 'desconocido':
                    continue

                raw_date = row.get('FECHA', row.get('Fecha', row.get('fecha', '')))
                formatted_date = format_date_ddmmyyyy(raw_date)
                
                row_data = []
                for target_col in official_headers:
                    if target_col in ['FECHA', 'Fecha']:
                        row_data.append(formatted_date)
                    elif target_col == 'HORAS TRABAJADAS (HH:MM)':
                        actual_col_name = col_map.get(target_col, 'HORAS TRABAJADAS (HH:MM)')
                        raw_val = row.get(actual_col_name, row.get('HORAS TRABAJADAS', 0.0))
                        row_data.append(format_hhmm_cell(raw_val, is_hours_float=True))
                    elif target_col == 'TARDANZA (HH:MM)':
                        actual_col_name = col_map.get(target_col, 'TARDANZA (HH:MM)')
                        raw_val = row.get(actual_col_name, row.get('TARDANZA (MIN)', 0))
                        row_data.append(format_hhmm_cell(raw_val, is_hours_float=False))
                    elif target_col == 'SALIDA ANTICIPADA (HH:MM)':
                        actual_col_name = col_map.get(target_col, 'SALIDA ANTICIPADA (HH:MM)')
                        raw_val = row.get(actual_col_name, row.get('SALIDA ANTICIPADA (MIN)', 0))
                        row_data.append(format_hhmm_cell(raw_val, is_hours_float=False))
                    elif target_col == 'EXCESO JORNADA (HH:MM)':
                        actual_col_name = col_map.get(target_col, 'EXCESO JORNADA (HH:MM)')
                        raw_val = row.get(actual_col_name, row.get('EXCESO JORNADA', 0))
                        row_data.append(format_hhmm_cell(raw_val, is_hours_float=False))
                    elif target_col == 'TOTAL HORAS ADICIONALES (HH:MM)':
                        actual_col_name = col_map.get(target_col, 'TOTAL HORAS ADICIONALES (HH:MM)')
                        raw_val = row.get(actual_col_name, row.get('TOTAL HORAS ADICIONALES', 0))
                        row_data.append(format_hhmm_cell(raw_val, is_hours_float=False))
                    elif target_col == 'DURACIÓN (HH:MM)':
                        actual_col_name = col_map.get(target_col, 'DURACIÓN (HH:MM)')
                        raw_val = row.get(actual_col_name, row.get('DURACIÓN', row.get('DURACION_MIN', 0)))
                        row_data.append(format_hhmm_cell(raw_val, is_hours_float=False))
                    else:
                        actual_col_name = col_map.get(target_col, target_col)
                        row_data.append(row.get(actual_col_name, ""))
                ws.append(row_data)
                
            # Auto-ajustar ancho de columnas
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
        else:
            for col in ws.columns:
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = 18

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()

def guardar_excel_base(
    df_trabajadores: pd.DataFrame,
    df_marcaciones: pd.DataFrame,
    df_asistencia: pd.DataFrame,
    df_horas_extra: pd.DataFrame,
    df_incidencias: pd.DataFrame,
    target_path: str = BASE_EXCEL_TEMPLATE
) -> bool:
    """Guarda directamente los resultados en el archivo Excel base en disco si no está bloqueado."""
    excel_bytes = exportar_asistencia_excel(
        df_trabajadores, df_marcaciones, df_asistencia, df_horas_extra, df_incidencias, target_path
    )
    try:
        with open(target_path, "wb") as f:
            f.write(excel_bytes)
        return True
    except PermissionError:
        print(f"[Warn] No se pudo sobrescribir '{target_path}' porque el archivo está abierto en Microsoft Excel. Guardando copia procesada.")
        alt_path = target_path.replace(".xlsm", "_procesado.xlsx")
        try:
            with open(alt_path, "wb") as f:
                f.write(excel_bytes)
        except Exception:
            pass
        return False
