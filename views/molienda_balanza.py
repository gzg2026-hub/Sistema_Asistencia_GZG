import streamlit as st
import sqlite3
import pandas as pd
import datetime
import os
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ruta de la base de datos de la balanza
def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    posibles_rutas = [
        os.path.join(base_dir, "pesajes.db"),
        r"C:\Users\GZG Minerales 2026\Desktop\GZG\Proyecto Balanza\pesajes.db",
        os.path.abspath(os.path.join(base_dir, "..", "Proyecto Balanza", "pesajes.db")),
    ]
    for r in posibles_rutas:
        if os.path.exists(r):
            return r
    return posibles_rutas[0]

RUTA_PESAJES_DB = get_db_path()

def obtener_conexion():
    if not os.path.exists(RUTA_PESAJES_DB):
        return None
    conn = sqlite3.connect(RUTA_PESAJES_DB)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_configuracion_planta():
    conn = obtener_conexion()
    if not conn:
        return {"factor_tph": 4.6, "humedad_pct": 0.0, "intervalo_muestreo_min": 15, "meta_tmd": 350.0}
    try:
        row = conn.execute("SELECT * FROM configuracion_planta WHERE id = 1").fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception:
        pass
    if conn:
        conn.close()
    return {"factor_tph": 4.6, "humedad_pct": 0.0, "intervalo_muestreo_min": 15, "meta_tmd": 350.0}

def guardar_configuracion_planta(factor_tph: float, humedad_pct: float, intervalo_min: int, meta_tmd: float):
    conn = obtener_conexion()
    if not conn:
        return False
    try:
        conn.execute("""
            INSERT INTO configuracion_planta (id, factor_tph, humedad_pct, intervalo_muestreo_min, meta_tmd, updated_at)
            VALUES (1, ?, ?, ?, ?, datetime('now', 'localtime'))
            ON CONFLICT(id) DO UPDATE SET
                factor_tph = excluded.factor_tph,
                humedad_pct = excluded.humedad_pct,
                intervalo_muestreo_min = excluded.intervalo_muestreo_min,
                meta_tmd = excluded.meta_tmd,
                updated_at = excluded.updated_at
        """, (factor_tph, humedad_pct, intervalo_min, meta_tmd))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if conn:
            conn.close()
        return False

def generar_excel_metalurgico(df_pesajes, df_paradas, config, kpis):
    """Genera reporte oficial de planta multi-hoja con openpyxl."""
    wb = openpyxl.Workbook()
    ws_resumen = wb.active
    ws_resumen.title = "Resumen Metalúrgico"
    ws_pesajes = wb.create_sheet(title="Pesajes Detallados")
    ws_paradas = wb.create_sheet(title="Paradas de Planta")

    font_titulo = Font(name="Arial", size=14, bold=True, color="FFFFFF")
    font_sec = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    font_header = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Arial", size=10, bold=True)
    font_data = Font(name="Arial", size=10)

    fill_azul = PatternFill(start_color="0A2540", end_color="0A2540", fill_type="solid")
    fill_naranja = PatternFill(start_color="F58220", end_color="F58220", fill_type="solid")
    fill_gris = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1. Hoja Resumen
    ws_resumen.merge_cells("A1:D1")
    c_tit = ws_resumen["A1"]
    c_tit.value = "GZG MINERALES - REPORTE METALÚRGICO DE MOLIENDA"
    c_tit.font = font_titulo
    c_tit.fill = fill_azul
    c_tit.alignment = Alignment(horizontal="center", vertical="center")
    ws_resumen.row_dimensions[1].height = 32

    ws_resumen["A3"] = "Fecha del Reporte:"
    ws_resumen["B3"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    ws_resumen["A4"] = "Meta Diaria (TMD):"
    ws_resumen["B4"] = config.get("meta_tmd", 350.0)
    ws_resumen["A5"] = "Factor K (tph):"
    ws_resumen["B5"] = config.get("factor_tph", 4.60)
    ws_resumen["A6"] = "Humedad (%):"
    ws_resumen["B6"] = config.get("humedad_pct", 0.0)

    ws_resumen["C3"] = "TMH Acumulada:"
    ws_resumen["D3"] = kpis.get("tmh", 0.0)
    ws_resumen["C4"] = "TMS Acumulada:"
    ws_resumen["D4"] = kpis.get("tms", 0.0)
    ws_resumen["C5"] = "Horas Operación:"
    ws_resumen["D5"] = kpis.get("hrs_marcha", 0.0)
    ws_resumen["C6"] = "Disponibilidad:"
    ws_resumen["D6"] = f"{kpis.get('disponibilidad', 0.0)} %"

    for r in range(3, 7):
        ws_resumen[f"A{r}"].font = font_bold
        ws_resumen[f"C{r}"].font = font_bold
        for c in ["A", "B", "C", "D"]:
            ws_resumen[f"{c}{r}"].border = thin_border

    # 2. Hoja Pesajes Detallados
    ws_pesajes.merge_cells("A1:H1")
    c_p = ws_pesajes["A1"]
    c_p.value = "REGISTRO DETALLADO DE PESAJES - BALANZA DE FAJA"
    c_p.font = font_titulo
    c_p.fill = fill_azul
    c_p.alignment = Alignment(horizontal="center", vertical="center")
    ws_pesajes.row_dimensions[1].height = 28

    headers_pesajes = ["FID", "Fecha / Hora", "Peso (kg)", "Muestra #", "Productor", "Campaña", "Material", "Operador"]
    for col_idx, h in enumerate(headers_pesajes, start=1):
        cell = ws_pesajes.cell(row=2, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_naranja
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws_pesajes.row_dimensions[2].height = 22

    if not df_pesajes.empty:
        for r_idx, row in enumerate(df_pesajes.itertuples(), start=3):
            vals = [
                getattr(row, "fid", ""),
                str(getattr(row, "fecha_balanza", "")),
                float(getattr(row, "peso_kg", 0.0) or 0.0),
                getattr(row, "numero_muestra", ""),
                getattr(row, "productor", ""),
                getattr(row, "campana", ""),
                getattr(row, "material", ""),
                getattr(row, "operador", "")
            ]
            for c_idx, val in enumerate(vals, start=1):
                cell = ws_pesajes.cell(row=r_idx, column=c_idx, value=val)
                cell.font = font_data
                cell.border = thin_border
                if r_idx % 2 == 0:
                    cell.fill = fill_zebra
                if c_idx == 3:
                    cell.number_format = '#,##0.0'
                    cell.alignment = Alignment(horizontal="right")
                elif c_idx in [1, 2, 4]:
                    cell.alignment = Alignment(horizontal="center")

    # 3. Hoja Paradas de Planta
    ws_paradas.merge_cells("A1:F1")
    c_par = ws_paradas["A1"]
    c_par.value = "REGISTRO DE PARADAS DE PLANTA"
    c_par.font = font_titulo
    c_par.fill = fill_azul
    c_par.alignment = Alignment(horizontal="center", vertical="center")
    ws_paradas.row_dimensions[1].height = 28

    headers_paradas = ["Tipo", "Motivo / Causa", "Hora Inicio", "Hora Fin", "Duración (min)", "Estado"]
    for col_idx, h in enumerate(headers_paradas, start=1):
        cell = ws_paradas.cell(row=2, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_gris
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws_paradas.row_dimensions[2].height = 22

    if not df_paradas.empty:
        for r_idx, row in enumerate(df_paradas.itertuples(), start=3):
            vals = [
                getattr(row, "tipo", ""),
                getattr(row, "motivo", ""),
                str(getattr(row, "ts_inicio", "")),
                str(getattr(row, "ts_fin", "") or "EN CURSO"),
                int(getattr(row, "duracion_minutos", 0) or 0),
                getattr(row, "estado", "")
            ]
            for c_idx, val in enumerate(vals, start=1):
                cell = ws_paradas.cell(row=r_idx, column=c_idx, value=val)
                cell.font = font_data
                cell.border = thin_border
                if r_idx % 2 == 0:
                    cell.fill = fill_zebra
                if c_idx == 5:
                    cell.alignment = Alignment(horizontal="right")
                elif c_idx in [1, 3, 4, 6]:
                    cell.alignment = Alignment(horizontal="center")

    # Autoajustar anchos
    for sheet in [ws_resumen, ws_pesajes, ws_paradas]:
        for col in sheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def render_molienda_balanza():
    """Renderiza el Módulo de Control de Balanza y Molienda para Superintendencia y Gerencia."""
    st.markdown("""
    <style>
        .gzg-molienda-card {
            background: rgba(26, 29, 36, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 14px;
        }
        .gzg-kpi-box {
            background: #1e2430;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 12px 14px;
            text-align: center;
        }
        .gzg-kpi-lbl {
            font-size: 11px;
            font-weight: 700;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 4px;
        }
        .gzg-kpi-val {
            font-size: 22px;
            font-weight: 900;
            color: #F58220;
            font-variant-numeric: tabular-nums;
        }
        .gzg-kpi-sub {
            font-size: 11px;
            color: #64748b;
            margin-top: 2px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Cabecera del Módulo
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #1A1D24 0%, #121418 100%); border: 1px solid rgba(245, 130, 32, 0.3); border-radius: 14px; padding: 14px 18px; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 30px;">⚖️</div>
            <div>
                <div style="font-size: 16px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px;">CONTROL DE BALANZA Y MOLIENDA</div>
                <div style="font-size: 11px; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px;">MONITOREO METALÚRGICO EN TIEMPO REAL - PLANTA GZG</div>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 10px; font-weight: 800; color: #F58220; background: rgba(245, 130, 32, 0.15); border: 1px solid rgba(245, 130, 32, 0.3); border-radius: 6px; padding: 3px 10px; text-transform: uppercase;">
                SUPERINTENDENCIA
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    conn = obtener_conexion()
    if not conn:
        st.error(f"⚠️ No se encontró la base de datos de la balanza en `{RUTA_PESAJES_DB}`. Verifique que el servicio de balanza esté ejecutándose.")
        return

    # Leer configuración de planta
    config = obtener_configuracion_planta()
    factor_k = float(config.get("factor_tph", 4.60))
    humedad_pct = float(config.get("humedad_pct", 0.0))
    intervalo_min = int(config.get("intervalo_muestreo_min", 15))
    meta_tmd = float(config.get("meta_tmd", 350.0))

    # Leer estado de lote activo
    lote = None
    try:
        r_lote = conn.execute("SELECT * FROM estado_lote WHERE id = 1").fetchone()
        if r_lote:
            lote = dict(r_lote)
    except Exception:
        pass

    # Leer si hay parada activa
    parada_activa = None
    try:
        r_parada = conn.execute("SELECT * FROM paradas WHERE estado = 'ACTIVA' ORDER BY id DESC LIMIT 1").fetchone()
        if r_parada:
            parada_activa = dict(r_parada)
    except Exception:
        pass

    # Leer pesajes de hoy o recientes
    try:
        df_pesajes = pd.read_sql_query("SELECT * FROM pesajes ORDER BY id DESC LIMIT 100", conn)
    except Exception:
        df_pesajes = pd.DataFrame()

    # Leer paradas
    try:
        df_paradas = pd.read_sql_query("SELECT * FROM paradas ORDER BY id DESC LIMIT 50", conn)
    except Exception:
        df_paradas = pd.DataFrame()

    conn.close()

    # ── 1. SEMÁFORO DE RITMO DE MUESTREO (15 MINUTOS) ─────────────────────────
    ultimo_ts = None
    minutos_desde_ultimo = 999
    if not df_pesajes.empty and 'fecha_balanza' in df_pesajes.columns:
        fecha_str = str(df_pesajes.iloc[0]['fecha_balanza']).strip()
        try:
            ultimo_ts = datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            ahora = datetime.datetime.now()
            minutos_desde_ultimo = int((ahora - ultimo_ts).total_seconds() / 60)
        except Exception:
            pass

    # Determinar estado del semáforo con umbral de 15 min
    if parada_activa:
        semaforo_color = "#ef4444"
        semaforo_bg = "rgba(239, 68, 68, 0.15)"
        semaforo_border = "#ef4444"
        semaforo_icono = "🛑"
        semaforo_titulo = "PLANTA DETENIDA - PARADA REGISTRADA"
        semaforo_desc = f"Motivo: <strong>{parada_activa.get('tipo', '')} - {parada_activa.get('motivo', '')}</strong> desde {parada_activa.get('ts_inicio', '')}"
    elif minutos_desde_ultimo <= intervalo_min:
        semaforo_color = "#4ade80"
        semaforo_bg = "rgba(74, 222, 128, 0.15)"
        semaforo_border = "#4ade80"
        semaforo_icono = "🟢"
        semaforo_titulo = "RITMO NORMAL DE MUESTREO"
        semaforo_desc = f"Último pesaje hace <strong>{minutos_desde_ultimo} min</strong> (Intervalo estándar: {intervalo_min} min)."
    elif minutos_desde_ultimo <= (intervalo_min + 10):
        semaforo_color = "#facc15"
        semaforo_bg = "rgba(250, 204, 21, 0.15)"
        semaforo_border = "#facc15"
        semaforo_icono = "🟡"
        semaforo_titulo = "RETRASO LEVE EN CORTE DE MUESTRA"
        semaforo_desc = f"Han transcurrido <strong>{minutos_desde_ultimo} min</strong> desde el último pesaje (Supera el límite de {intervalo_min} min)."
    else:
        semaforo_color = "#f87171"
        semaforo_bg = "rgba(248, 113, 113, 0.18)"
        semaforo_border = "#f87171"
        semaforo_icono = "🔴"
        semaforo_titulo = "ALERTA CRÍTICA: RETRASO EN MUESTREO"
        semaforo_desc = f"¡ALERTA! Más de <strong>{minutos_desde_ultimo} min</strong> sin pesar. Verificar corte de muestra con el operador o posible detención de faja."

    st.markdown(f"""
    <div style="background: {semaforo_bg}; border: 1.5px solid {semaforo_border}; border-radius: 12px; padding: 14px 18px; margin-bottom: 16px; display: flex; align-items: center; gap: 14px;">
        <div style="font-size: 32px;">{semaforo_icono}</div>
        <div style="flex: 1;">
            <div style="font-size: 14px; font-weight: 900; color: {semaforo_color}; letter-spacing: 0.5px;">{semaforo_titulo}</div>
            <div style="font-size: 12px; color: #E2E8F0; margin-top: 3px;">{semaforo_desc}</div>
        </div>
        <div style="text-align: right; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 14px;">
            <div style="font-size: 10px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Último Pesaje</div>
            <div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">{ultimo_ts.strftime('%H:%M:%S') if ultimo_ts else 'Sin registro'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. CÁLCULO DE KPIS METALÚRGICOS ─────────────────────────────────────────
    total_kg = float(df_pesajes['peso_kg'].sum()) if not df_pesajes.empty else 0.0
    tmh = round(total_kg / 1000.0, 2)
    # TMS con descuento por humedad
    tms = round(tmh * (1.0 - (humedad_pct / 100.0)), 2)
    total_pesajes = len(df_pesajes)

    # Minutos de paradas acumuladas
    minutos_paradas = 0
    if not df_paradas.empty and 'duracion_minutos' in df_paradas.columns:
        minutos_paradas = int(df_paradas['duracion_minutos'].fillna(0).sum())

    # Disponibilidad aproximada (sobre base de 24h = 1440 min)
    minutos_dia = 1440
    minutos_marcha = max(0, minutos_dia - minutos_paradas)
    disponibilidad = round((minutos_marcha / minutos_dia) * 100.0, 1)
    hrs_marcha = round(minutos_marcha / 60.0, 1)

    # TPH calculado sobre marcha
    tph_real = round(tmh / hrs_marcha, 2) if hrs_marcha > 0 else 0.0
    cumplimiento_meta = round((tmh / meta_tmd * 100.0), 1) if meta_tmd > 0 else 0.0

    kpis_dict = {
        "tmh": tmh,
        "tms": tms,
        "tph": tph_real,
        "hrs_marcha": hrs_marcha,
        "disponibilidad": disponibilidad,
        "total_pesajes": total_pesajes
    }

    # Grid de KPIs principales
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="gzg-kpi-box">
            <div class="gzg-kpi-lbl">TMH Acumulado</div>
            <div class="gzg-kpi-val">{tmh:,.2f}</div>
            <div class="gzg-kpi-sub">Toneladas Húmedas</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="gzg-kpi-box" style="border-color: rgba(56, 189, 248, 0.4);">
            <div class="gzg-kpi-lbl">TMS (Secas)</div>
            <div class="gzg-kpi-val" style="color: #38bdf8;">{tms:,.2f}</div>
            <div class="gzg-kpi-sub">Humedad: {humedad_pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="gzg-kpi-box">
            <div class="gzg-kpi-lbl">Factor K Planta</div>
            <div class="gzg-kpi-val" style="color: #facc15;">{factor_k:.2f}</div>
            <div class="gzg-kpi-sub">tph constante</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="gzg-kpi-box">
            <div class="gzg-kpi-lbl">Disponibilidad</div>
            <div class="gzg-kpi-val" style="color: {'#4ade80' if disponibilidad >= 90 else '#facc15'};">{disponibilidad}%</div>
            <div class="gzg-kpi-sub">{hrs_marcha}h marcha / {round(minutos_paradas/60.0, 1)}h paradas</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="gzg-kpi-box">
            <div class="gzg-kpi-lbl">Meta Diaria</div>
            <div class="gzg-kpi-val" style="color: #a78bfa;">{cumplimiento_meta}%</div>
            <div class="gzg-kpi-sub">Meta: {meta_tmd:,.0f} TMD</div>
        </div>
        """, unsafe_allow_html=True)

    # ── 3. RESUMEN DEL LOTE ACTIVO ─────────────────────────────────────────────
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    if lote:
        st.markdown(f"""
        <div class="gzg-molienda-card" style="border-left: 4px solid #F58220;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 12px; font-weight: 800; color: #F58220; text-transform: uppercase; letter-spacing: 1px;">Lote Activo en Molienda</span>
                <span style="font-size: 11px; font-weight: 700; color: #94a3b8; background: #1e2430; padding: 2px 8px; border-radius: 6px;">Turno: {lote.get('turno', 'N/A')}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;">
                <div><div style="font-size: 10px; color: #94a3b8; font-weight: 700;">PRODUCTOR</div><div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">{lote.get('productor', 'N/A')}</div></div>
                <div><div style="font-size: 10px; color: #94a3b8; font-weight: 700;">CAMPAÑA</div><div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">{lote.get('campana', 'N/A')}</div></div>
                <div><div style="font-size: 10px; color: #94a3b8; font-weight: 700;">MATERIAL</div><div style="font-size: 13px; font-weight: 800; color: #38bdf8;">{lote.get('material', 'N/A')}</div></div>
                <div><div style="font-size: 10px; color: #94a3b8; font-weight: 700;">OPERADOR BALANZA</div><div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">{lote.get('operador', 'N/A')}</div></div>
                <div><div style="font-size: 10px; color: #94a3b8; font-weight: 700;">MUESTRA ACTUAL</div><div style="font-size: 13px; font-weight: 800; color: #4ade80;">#{lote.get('numero_muestra', 0)}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── 4. PANEL DE CONFIGURACIÓN DE PARÁMETROS (EXCLUSIVO SUPERINTENDENCIA) ───
    with st.expander("⚙️ Ajustes Metalúrgicos de Planta (Factor K, Humedad, Meta TMD)", expanded=False):
        st.markdown("<p style='font-size: 12px; color: #94a3b8;'>Modifique los parámetros según la calibración o variaciones operativas. Los cambios se sincronizan en tiempo real.</p>", unsafe_allow_html=True)
        with st.form("frm_config_planta_super"):
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                n_factor_k = st.number_input("Factor K (tph constante)", value=factor_k, step=0.1, format="%.2f", help="Factor multiplicador estándar de calibración (ej. 4.60)")
            with col_f2:
                n_humedad = st.number_input("Humedad del Mineral (%)", value=humedad_pct, step=0.5, format="%.1f", help="Porcentaje de humedad para descontar TMH y obtener TMS")
            with col_f3:
                n_intervalo = st.number_input("Intervalo de Muestreo (min)", value=intervalo_min, step=1, min_value=5, max_value=60, help="Intervalo esperado entre pesajes para el semáforo (ej. 15 min)")
            with col_f4:
                n_meta_tmd = st.number_input("Meta Diaria de Planta (TMD)", value=meta_tmd, step=25.0, format="%.0f", help="Meta diaria presupuestada en Toneladas Métricas")

            btn_guardar_cfg = st.form_submit_button("💾 Guardar Parámetros de Planta", type="primary")
            if btn_guardar_cfg:
                ok = guardar_configuracion_planta(n_factor_k, n_humedad, n_intervalo, n_meta_tmd)
                if ok:
                    st.toast("✅ Parámetros de planta actualizados correctamente", icon="⚙️")
                    st.success(f"Configuración guardada: Factor K = {n_factor_k:.2f} | Humedad = {n_humedad:.1f}% | Intervalo = {n_intervalo} min")
                    st.rerun()
                else:
                    st.error("Error al guardar la configuración en la base de datos.")

    # ── 5. DESCARGA DE REPORTE EXCEL METALÚRGICO ───────────────────────────────
    col_btn_excel, col_btn_refresh = st.columns([1.2, 0.4])
    with col_btn_excel:
        excel_bytes = generar_excel_metalurgico(df_pesajes, df_paradas, config, kpis_dict)
        nom_archivo = f"Reporte_Metalurgico_GZG_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
        st.download_button(
            label="📊 Descargar Reporte Oficial Excel (.xlsx)",
            data=excel_bytes,
            file_name=nom_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col_btn_refresh:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.rerun()

    # ── 6. PESTAÑAS DE DETALLES: PESAJES Y PARADAS ─────────────────────────────
    tab_p, tab_par = st.tabs(["📋 Últimos Pesajes Registrados", "🛑 Historial de Paradas de Planta"])

    with tab_p:
        if not df_pesajes.empty:
            cols_ver = [c for c in ['fid', 'fecha_balanza', 'peso_kg', 'numero_muestra', 'productor', 'campana', 'material', 'operador'] if c in df_pesajes.columns]
            df_mostrar = df_pesajes[cols_ver].copy()
            df_mostrar.rename(columns={
                'fid': 'FID',
                'fecha_balanza': 'Fecha / Hora',
                'peso_kg': 'Peso (kg)',
                'numero_muestra': 'Muestra #',
                'productor': 'Productor',
                'campana': 'Campaña',
                'material': 'Material',
                'operador': 'Operador'
            }, inplace=True)
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        else:
            st.info("No hay pesajes registrados en la base de datos.")

    with tab_par:
        if not df_paradas.empty:
            cols_par = [c for c in ['tipo', 'motivo', 'ts_inicio', 'ts_fin', 'duracion_minutos', 'operador', 'estado'] if c in df_paradas.columns]
            df_par_mostrar = df_paradas[cols_par].copy()
            df_par_mostrar.rename(columns={
                'tipo': 'Tipo',
                'motivo': 'Motivo / Causa',
                'ts_inicio': 'Hora Inicio',
                'ts_fin': 'Hora Fin',
                'duracion_minutos': 'Duración (min)',
                'operador': 'Operador',
                'estado': 'Estado'
            }, inplace=True)
            st.dataframe(df_par_mostrar, use_container_width=True, hide_index=True)
        else:
            st.info("Sin registros de paradas de planta.")
