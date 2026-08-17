import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
from datetime import datetime, date, timezone, timedelta
from core.config import AttendanceConfig
from core.attendance_engine import procesar_asistencia_df
from data.data_loader import cargar_datos_excel
from data.exporter import exportar_asistencia_excel, guardar_excel_base
from data.database import (
    init_db, guardar_trabajadores, guardar_marcaciones_raw,
    guardar_asistencia_y_reportes, obtener_datos_db,
    obtener_todos_usuarios, crear_usuario, eliminar_usuario,
    actualizar_estado_he, actualizar_estado_incidencia
)
from core.auth import (
    init_auth, is_authenticated, login_user, logout_user, get_current_user, hash_password
)
from scripts.generate_test_transactions import generar_lote_pruebas

st.set_page_config(
    page_title="GZG Minerales - Control de Asistencia",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialización diferida - se ejecuta solo una vez vía cache

def get_logo_base64(logo_path="assets/gzg_logo_transparent.png"):
    """Convierte el logo corporativo transparente de GZG a Base64 para incrustar en HTML."""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    elif os.path.exists("assets/gzg_logo.png"):
        with open("assets/gzg_logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def format_hhmm(minutes) -> str:
    if pd.isna(minutes) or minutes is None or minutes <= 0:
        return "00:00"
    m = int(minutes)
    hrs = m // 60
    mins = m % 60
    return f"{hrs:02d}:{mins:02d}"

def to_numeric_minutes(series) -> pd.Series:
    """Convierte de forma ultra-segura y vectorizada cualquier Serie (HH:MM, int, float, str, NaN) a minutos flotantes."""
    if series is None or (isinstance(series, pd.Series) and series.empty):
        return pd.Series(dtype=float)
    
    s = pd.Series(series) if not isinstance(series, pd.Series) else series.copy()
    num_s = pd.to_numeric(s, errors='coerce')
    
    mask_nan = num_s.isna() & s.notna()
    if mask_nan.any():
        str_s = s[mask_nan].astype(str).str.strip()
        split_df = str_s.str.split(':', expand=True)
        if split_df.shape[1] >= 2:
            h = pd.to_numeric(split_df[0], errors='coerce').fillna(0)
            m = pd.to_numeric(split_df[1], errors='coerce').fillna(0)
            num_s[mask_nan] = h * 60.0 + m
            
    return num_s.fillna(0.0)

def _inject_dashboard_css():
    """Inyecta el CSS completo del dashboard. Solo se llama cuando el usuario está autenticado."""
    st.markdown("""
<style>
    /* Theme Base Oscuro (#090a0f) */
    .stApp, [data-testid="stMain"] {
        background-color: #090a0f !important;
        color: #ffffff;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        transition: none !important;
        animation: none !important;
    }

    section[data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarCollapsedControl"] {
        transition: none !important;
        animation: none !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding-top: 2.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-bottom: 2rem !important;
        width: 100% !important;
    }

    /* OCULTAR COMPLETAMENTE MENÚ DERECHO, SHARE, STAR, EDIT, GITHUB Y FOOTER DE LA ESQUINA SUPERIOR DERECHA */
    #MainMenu,
    footer,
    .stDeployButton,
    .stAppToolbar,
    div[data-testid="stMainMenu"],
    div[data-testid="stStatusWidget"],
    div[data-testid="stFooter"],
    div[data-testid="stToolbar"],
    div[data-testid="stHeaderActionElements"],
    [data-testid="stHeader"] a,
    [data-testid="stHeader"] div:not([data-testid="stSidebarCollapsedControl"]) {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* OCULTAR INSTRUCCIONES SECUNDARIAS DE INPUTS DE FORMA DEFINITIVA */
    [data-testid="stInputInstructions"],
    div[data-testid="stInputInstructions"],
    small[data-testid="stInputInstructions"],
    span[data-testid="stInputInstructions"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        color: transparent !important;
        -webkit-text-fill-color: transparent !important;
        font-size: 0px !important;
        height: 0px !important;
        width: 0px !important;
        position: absolute !important;
        top: -9999px !important;
        left: -9999px !important;
        pointer-events: none !important;
    }

    /* BARRA CABECERA TRANSPARENTE */
    header[data-testid="stHeader"], div[data-testid="stHeader"], .stAppHeader {
        background: transparent !important;
        z-index: 99999 !important;
    }

    /* BOTÓN TOGGLE SIDEBAR */
    div[data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarExpandButton"] {
        background-color: #11131c !important;
        border: 1.5px solid #c58b4e !important;
        border-radius: 12px !important;
        width: 44px !important;
        height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 999999 !important;
    }

    div[data-testid="stSidebarCollapsedControl"]:hover,
    button[data-testid="stSidebarCollapseButton"]:hover,
    button[data-testid="stSidebarExpandButton"]:hover {
        background-color: #1c1e29 !important;
        border-color: #f59e0b !important;
        box-shadow: 0 0 18px rgba(245, 158, 11, 0.85) !important;
    }

    /* ICONO INTERNO EN ESTADO ESTÁTICO - AMBAS FLECHAS EXACTAMENTE EN 24px */
    div[data-testid="stSidebarCollapsedControl"] *,
    [data-testid="stSidebarCollapsedControl"] *,
    div[data-testid="collapsedControl"] *,
    header[data-testid="stHeader"] button *,
    div[data-testid="stHeader"] button *,
    button[data-testid="stBaseButton-header"] *,
    button[data-testid="stHeaderCollapseButton"] *,
    button[data-testid="stSidebarCollapseButton"] *,
    button[data-testid="stSidebarExpandButton"] *,
    [data-testid="stSidebarHeader"] button *,
    button[aria-label*="Expand"] *,
    button[aria-label*="expand"] *,
    button[aria-label*="Sidebar"] *,
    button[aria-label*="sidebar"] * {
        fill: #ffffff !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        min-height: 24px !important;
        max-width: 24px !important;
        max-height: 24px !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transform: none !important; /* Exactamente 24px en ambos estados */
        opacity: 1 !important;
        margin: auto !important;
        pointer-events: none !important;
        filter: none !important;
        transition: all 0.25s ease !important;
    }

    /* HOVER (SOLO AL ACERCAR EL MOUSE): BRILLO NEÓN DORADO ÁMBAR INTENSO */
    div[data-testid="stSidebarCollapsedControl"]:hover,
    header[data-testid="stHeader"] button:hover,
    div[data-testid="stHeader"] button:hover,
    button[data-testid="stBaseButton-header"]:hover,
    button[data-testid="stHeaderCollapseButton"]:hover,
    button[data-testid="stSidebarCollapseButton"]:hover,
    button[data-testid="stSidebarExpandButton"]:hover,
    [data-testid="stSidebarHeader"] button:hover {
        background-color: #1c1e29 !important;
        background: #1c1e29 !important;
        border-color: #f59e0b !important;
        box-shadow: 0 0 18px rgba(245, 158, 11, 0.85), 0 0 10px rgba(251, 191, 36, 0.7), inset 0 0 6px rgba(245, 158, 11, 0.3) !important;
    }

    div[data-testid="stSidebarCollapsedControl"]:hover *,
    header[data-testid="stHeader"] button:hover *,
    div[data-testid="stHeader"] button:hover *,
    button[data-testid="stBaseButton-header"]:hover *,
    button[data-testid="stHeaderCollapseButton"]:hover *,
    button[data-testid="stSidebarCollapseButton"]:hover *,
    button[data-testid="stSidebarExpandButton"]:hover *,
    [data-testid="stSidebarHeader"] button:hover * {
        fill: #f59e0b !important;
        stroke: #f59e0b !important;
        color: #f59e0b !important;
        filter: drop-shadow(0 0 4px rgba(245, 158, 11, 0.85)) !important;
    }

    /* RESTAURAR BOTONES DE ACCIÓN DEL SIDEBAR (FILTRAR, GENERAR LOTE DE PRUEBAS) A ANCHO COMPLETO */
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        height: auto !important;
        min-height: 44px !important;
        max-width: 100% !important;
        max-height: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        word-break: normal !important;
        font-size: 0.95rem !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        padding: 0.65rem 1rem !important;
        margin: 0.5rem 0 !important;
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border: 1px solid #0369a1 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
    }

    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #0369a1 !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4) !important;
    }
    
    /* Main Header Container */
    .main-header-cajon {
        background: #090a0f;
        border: 1px solid #1c1e29;
        border-top: 3px solid #c58b4e;
        border-radius: 14px;
        padding: 1rem 1.75rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.95), inset 0 1.5px 1px rgba(197, 139, 78, 0.4);
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .main-header-cajon:hover {
        border-top-color: #f59e0b;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.95), inset 0 2px 6px rgba(245, 158, 11, 0.6), 0 0 16px rgba(245, 158, 11, 0.35);
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .header-logo {
        height: 88px;
        width: auto;
        object-fit: contain;
        filter: drop-shadow(0 3px 10px rgba(197, 139, 78, 0.55));
    }
    .brand-block {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        line-height: 0.92;
    }
    /* GZG del Mismo Tono Bronce-Cobre Metálico del Logo Emblem */
    .brand-gzg {
        font-size: 2.75rem;
        font-weight: 900;
        color: #c58b4e;
        letter-spacing: 0.06em;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9);
    }
    /* Palabra MINERALES separada más abajo */
    .brand-minerales {
        font-size: 0.92rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 0.34em;
        margin-top: 10px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.9);
    }
    .header-divider {
        width: 2px;
        height: 56px;
        background: linear-gradient(180deg, transparent, #c58b4e, transparent);
        margin: 0 10px;
    }
    .main-title-text {
        color: #ffffff;
        font-size: 1.95rem;
        font-weight: 900;
        letter-spacing: -0.01em;
        line-height: 1.1;
    }
    
    /* Widgets del Encabezado */
    .header-widgets {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .widget-box-equal {
        background: #050608;
        border: 1px solid #1c1e29;
        border-top: 2.5px solid #c58b4e;
        border-radius: 12px;
        padding: 0.6rem 0.85rem;
        text-align: center;
        width: 160px;
        height: 68px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 1px 1px rgba(197, 139, 78, 0.3), 0 4px 10px rgba(0, 0, 0, 0.8);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
        overflow: hidden;
    }
    .widget-box-equal:hover {
        border-top-color: #f59e0b;
        box-shadow: inset 0 1.5px 4px rgba(245, 158, 11, 0.6), 0 0 12px rgba(245, 158, 11, 0.3);
    }
    .widget-label {
        font-size: 0.68rem;
        color: #94a3b8;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        line-height: 1;
        text-align: center;
        width: 100%;
        margin-bottom: 6px;
    }
    .widget-val {
        font-size: 1.15rem;
        color: #ffffff;
        font-weight: 800;
        line-height: 1;
        text-align: center;
        width: 100%;
    }
    
    /* SIDEBAR CON LA PALETA DE COLORES GZG MINERALES (DARK EXECUTIVE) */
    section[data-testid="stSidebar"] {
        background-color: #090a0f !important;
        background: #090a0f !important;
        border-right: 1.5px solid #1c1e29 !important;
    }

    /* Título principal del Panel de Control */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] .stMarkdown h1 {
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 1.4rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 0.5rem !important;
    }

    /* Subtítulos de sección limpios */
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #f59e0b !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0 !important;
        border-top: none !important;
    }

    /* Única Línea Fina Elegante de Separación de Sección (1px dorado #c58b4e) */
    section[data-testid="stSidebar"] hr {
        border: none !important;
        border-top: 1px solid rgba(197, 139, 78, 0.55) !important;
        margin: 1.25rem 0 0.5rem 0 !important;
        opacity: 1 !important;
    }

    /* Textos, Labels y Párrafos en Sidebar */
    .sidebar-field-title,
    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        margin-bottom: 4px !important;
        margin-top: 4px !important;
        line-height: 1.3 !important;
        display: block !important;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    /* =========================================================================
       FORMATO DE CAJÓN UNIFICADO CON ILUMINACIÓN DORADA PERMANENTE
       (100% Idéntico para Cargos, Trabajador, Fechas y Rutas en Sidebar)
       ========================================================================= */

    /* 1. CAJÓN SELECTOR DE CARGOS (Popover Button) */
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] button {
        background-color: #11131c !important;
        background: #11131c !important;
        border: 1.5px solid #dfa86a !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        height: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;
        padding: 0 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
        box-sizing: border-box !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }

    /* 2. CAJÓN SELECTOR DE TRABAJADOR Y SELECTBOXES */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] label,
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        margin-bottom: 4px !important;
        padding: 0 !important;
        display: block !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] {
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #11131c !important;
        background: #11131c !important;
        border: 1.5px solid #dfa86a !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        height: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;
        padding: 0 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.3s ease !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div * {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"] {
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
        margin-left: 6px !important;
    }

    /* 3. CAJÓN DE FECHAS Y TEXT INPUTS (DateInput y TextInput) */
    section[data-testid="stSidebar"] div[data-baseweb="base-input"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stDateInput"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #11131c !important;
        background: #11131c !important;
        border: 1.5px solid #dfa86a !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        height: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;
        padding: 0 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.3s ease !important;
    }

    /* 4. HOVER Y FOCUS: AQUÍ ES DONDE SE ENCIENDE EL BRILLO DORADO AL ACERCAR EL MOUSE */
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button:hover,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] button:hover,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button:focus,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] button:focus,
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    section[data-testid="stSidebar"] div[data-testid="stDateInput"] div[data-baseweb="input"]:hover,
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-baseweb="input"]:hover {
        border-color: #f59e0b !important;
        box-shadow: 0 0 16px rgba(245, 158, 11, 0.75) !important;
        background-color: #11131c !important;
        background: #11131c !important;
    }

    /* Estilos Popover Selector de Cargos con Casillas */
    div[data-testid="stPopover"] {
        width: 100% !important;
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stPopoverBody"],
    div[data-testid="stPopoverContent"] {
        background-color: #11131c !important;
        background: #11131c !important;
        border: 1.5px solid #c58b4e !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.95) !important;
        padding: 12px !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stCheckbox"] label p,
    div[data-testid="stPopoverContent"] div[data-testid="stCheckbox"] label p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.90rem !important;
    }

    /* Estilos de Textos dentro de los Cajones */
    section[data-testid="stSidebar"] input[type="text"], 
    section[data-testid="stSidebar"] input[type="date"] {
        color: #ffffff !important;
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        font-size: 0.90rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] p,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button span,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button p,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] button span,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] button p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.90rem !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] svg,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] svg {
        fill: #dfa86a !important;
        color: #dfa86a !important;
    }

    /* OCULTAR DEFINITIVAMENTE 'Press Enter to submit form' / 'Press Enter to apply' EN TODO EL SISTEMA */
    [data-testid="InputInstructions"],
    [data-testid="stInputInstructions"],
    div[data-testid="InputInstructions"],
    div[data-testid="stInputInstructions"],
    small[data-testid="InputInstructions"],
    small[data-testid="stInputInstructions"],
    span[data-testid="InputInstructions"],
    span[data-testid="stInputInstructions"],
    p[data-testid="InputInstructions"],
    div[data-testid="stTextInput"] [data-testid="InputInstructions"],
    div[data-testid="stTextInput"] [data-testid="stInputInstructions"],
    div[data-testid="stTextInput"] small,
    div[data-baseweb="input"] > div:not(:first-child),
    div[data-baseweb="input"] small,
    div[data-baseweb="base-input"] > div:not(:first-child),
    div[data-baseweb="base-input"] small,
    div[data-baseweb="base-input"] + div,
    [class*="InputInstructions"],
    [class*="inputInstructions"],
    [class*="instructions"],
    [class*="Instructions"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        color: transparent !important;
        -webkit-text-fill-color: transparent !important;
        font-size: 0px !important;
        line-height: 0 !important;
        height: 0px !important;
        width: 0px !important;
        margin: 0 !important;
        padding: 0 !important;
        position: absolute !important;
        top: -9999px !important;
        left: -9999px !important;
        pointer-events: none !important;
    }

    /* ELIMINAR EFECTO DE OSCURECIMIENTO / PARPADEO DE STREAMLIT AL INTERACTUAR */
    *[data-stale="true"],
    div[data-stale="true"],
    .stApp[data-stale="true"] main,
    div[data-testid="stMainBlockContainer"][data-stale="true"],
    section.main[data-stale="true"],
    div[data-testid="stAppViewContainer"][data-stale="true"] {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }

    /* PORTAL POPOVER MENÚ DESPLEGABLE ATADO AL BODY */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #11131c !important;
        background: #11131c !important;
        border: 1.5px solid #c58b4e !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.95) !important;
        z-index: 999999 !important;
    }

    li[role="option"],
    div[data-baseweb="option"] {
        background-color: #11131c !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 8px 12px !important;
    }

    li[role="option"] *,
    div[data-baseweb="option"] * {
        color: #ffffff !important;
    }

    li[role="option"]:hover,
    div[data-baseweb="option"]:hover,
    li[aria-selected="true"],
    div[aria-selected="true"] {
        background-color: #1c1e29 !important;
        color: #f59e0b !important;
    }

    li[role="option"]:hover *,
    div[data-baseweb="option"]:hover *,
    li[aria-selected="true"] * {
        color: #f59e0b !important;
    }

    section[data-testid="stSidebar"] div[role="combobox"]:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.4) !important;
    }

    /* File Uploader en Sidebar */
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] {
        background-color: #11131c !important;
        border: 1.5px dashed #333952 !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }

    /* Líneas separadoras hr en Sidebar con Borde Dorado GZG (#c58b4e) */
    section[data-testid="stSidebar"] hr {
        border: none !important;
        border-top: 3px solid #c58b4e !important;
        margin: 1.5rem 0 !important;
        opacity: 1 !important;
        box-shadow: 0 2px 8px rgba(197, 139, 78, 0.4) !important;
    }

    /* Limpiar bordes de formulario en sidebar */
    section[data-testid="stSidebar"] div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* Action Buttons (SIN MARCO CAJÓN DE NINGÚN TIPO) */
    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4) !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 1.05rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(22, 163, 74, 0.5) !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important;
    }

    /* RESTABLECER COLUMNAS ESTÁNDAR A ESTADO TRANSPARENTE */
    div[data-testid="stColumn"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        transform: none !important;
    }

    /* TARJETAS KPI SUPERIORES EN GRID ATÓMICO (CARGA INSTANTÁNEA SIN POP-IN) */
    .kpi-grid-container {
        display: grid !important;
        grid-template-columns: repeat(8, minmax(0, 1fr)) !important;
        gap: 12px !important;
        width: 100% !important;
        margin-bottom: 20px !important;
    }
    @media (max-width: 1500px) {
        .kpi-grid-container {
            grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
        }
    }
    @media (max-width: 800px) {
        .kpi-grid-container {
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        }
    }

    .kpi-cajon-single {
        background: #090a0f;
        border: 1px solid #1c1e29;
        border-top: 3px solid #c58b4e;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        box-shadow: 0 6px 22px rgba(0, 0, 0, 0.95), inset 0 1.5px 1px rgba(197, 139, 78, 0.4);
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 12px;
        min-height: 110px;
        width: 100%;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-cajon-single:hover {
        transform: translateY(-4px);
        border-top-color: #f59e0b;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.95), inset 0 2.5px 6px rgba(245, 158, 11, 0.75), 0 0 22px rgba(245, 158, 11, 0.5);
    }
    
    .kpi-icon-badge {
        width: 58px;
        height: 58px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: inset 0 1px 3px rgba(255, 255, 255, 0.2);
    }
    
    .kpi-text-block {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        overflow: hidden;
        width: 100%;
    }
    
    .kpi-cajon-single-title {
        font-size: 16px;
        font-weight: 900;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        line-height: 1.15;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: center;
        width: 100%;
    }
    
    .kpi-cajon-single-number {
        font-size: 37px;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.0;
        margin-top: 4px;
        text-align: center;
        letter-spacing: -0.02em;
        text-shadow: 0 3px 10px rgba(0, 0, 0, 0.9);
        width: 100%;
    }
    
    .kpi-cajon-single-number-sm {
        font-size: 28px;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.0;
        margin-top: 4px;
        text-align: center;
        letter-spacing: -0.02em;
        text-shadow: 0 3px 10px rgba(0, 0, 0, 0.9);
        width: 100%;
    }

    /* UNICO CAJÓN 3D PARA LOS 2 GRÁFICOS INFERIORES CON TÍTULOS Y LUZ GLOW HOVER */
    div[data-testid="stColumn"]:has(div[data-testid="stPlotlyChart"]) {
        background-color: #090a0f !important;
        background: #090a0f !important;
        border-radius: 14px !important;
        border-top: 3px solid #c58b4e !important;
        border-left: 1px solid #1c1e29 !important;
        border-right: 1px solid #1c1e29 !important;
        border-bottom: 1px solid #1c1e29 !important;
        box-shadow: 
            0 6px 20px rgba(0, 0, 0, 0.95), 
            inset 0 1.5px 1px rgba(197, 139, 78, 0.4) !important;
        padding: 1.25rem 1.25rem 0.5rem 1.25rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        transform: none !important;
        contain: none !important;
    }

    div[data-testid="stColumn"]:has(div[data-testid="stPlotlyChart"]):hover {
        border-top-color: #f59e0b !important;
        box-shadow: 
            0 12px 28px rgba(0, 0, 0, 0.95), 
            inset 0 2.5px 6px rgba(245, 158, 11, 0.75),
            0 0 18px rgba(245, 158, 11, 0.45) !important;
    }

    /* PANTALLA COMPLETA REAL EN TODO EL NAVEGADOR SIN BUCLES DE REFRESCO */
    div[data-testid="stPlotlyChart"]:fullscreen,
    div[data-testid="stPlotlyChart"]:-webkit-full-screen,
    div[data-testid="stPlotlyChart"]:-moz-full-screen {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 999999 !important;
        background-color: #090a0f !important;
        padding: 2rem !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }

    /* Título del KPI Gráfico Centrado Horizontalmente */
    .section-title {
        color: #ffffff !important;
        font-size: 1.45rem;
        font-weight: 900;
        margin-top: 0.1rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        gap: 8px;
    }

    /* TOP 10 Y ESTADÍSTICAS POR CARGO */
    .top10-container {
        background: #090a0f;
        border: 1px solid #1c1e29;
        border-top: 3px solid #c58b4e;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.95), inset 0 1.5px 1px rgba(197, 139, 78, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1.5rem;
    }
    .top10-container:hover {
        transform: translateY(-3px);
        border-top-color: #f59e0b;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.95), inset 0 2px 4px rgba(245, 158, 11, 0.6), 0 0 14px rgba(245, 158, 11, 0.3);
    }
    .top10-title-yellow {
        color: #f59e0b;
        font-size: 1.35rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.95rem;
        text-align: center;
    }
    .top10-title-blue {
        color: #3b82f6;
        font-size: 1.35rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.95rem;
        text-align: center;
    }
    .top10-title-red {
        color: #ef4444;
        font-size: 1.35rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.95rem;
        text-align: center;
    }
    .top10-table-custom {
        width: 100%;
        border-collapse: collapse;
        color: #ffffff;
    }
    .top10-table-custom th {
        background: #11131c;
        color: #cbd5e1;
        font-weight: 900;
        padding: 10px 8px;
        border-bottom: 1.5px solid #222638;
        text-transform: uppercase;
        font-size: 0.98rem;
        letter-spacing: 0.5px;
        text-align: center !important;
    }
    .top10-table-custom td {
        padding: 10px 8px;
        border-bottom: 1px solid #181a27;
        color: #f8fafc;
        font-weight: 700;
        font-size: 1.05rem;
        text-align: center !important;
    }
    .top10-table-custom tr:hover {
        background-color: #161926;
    }
    .top10-num {
        color: #ffffff !important;
        font-weight: 900;
        text-align: center !important;
        font-size: 1.15rem;
    }
    /* CONTENEDOR FLOTANTE DE POPOVERS (Cargos y Trabajadores) CON ALTURA MÁXIMA COMPACTA */
    [data-testid="stPopoverBody"],
    [data-testid="stPopoverContent"],
    div[data-baseweb="popover"] > div {
        max-height: 260px !important;
        overflow-y: auto !important;
        background-color: #0d0f17 !important;
        border: 1.5px solid #dfa86a !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important;
    }
    /* BOTONES DENTRO DEL DESPLEGABLE POPOVER (Cargos y Trabajadores) */
    [data-testid="stPopoverBody"] button,
    [data-testid="stPopoverContent"] button {
        white-space: nowrap !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 0.4rem 0.6rem !important;
        height: auto !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        color: #ffffff !important;
        background-color: #11131c !important;
        border: 1px solid #222638 !important;
        border-radius: 6px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }
    [data-testid="stPopoverBody"] button:hover,
    [data-testid="stPopoverContent"] button:hover {
        background-color: #1a1e2e !important;
        border-color: #dfa86a !important;
        color: #dfa86a !important;
    }
    [data-testid="stPopoverBody"] button *,
    [data-testid="stPopoverContent"] button * {
        color: #ffffff !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        margin: 0 !important;
        padding: 0 !important;
        text-align: left !important;
    }
    [data-testid="stPopoverBody"] button:hover *,
    [data-testid="stPopoverContent"] button:hover * {
        color: #dfa86a !important;
    }
</style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# ---------------------------------------------------------
# AUTO-SEEDA EN MEMORIA ONCE AT BOOT (RESPUESTA INSTANTÁNEA EN LOGIN)
# ---------------------------------------------------------
@st.cache_resource
def init_app_boot_once():
    try:
        init_db()
        init_auth()
    except Exception as e:
        print(f"Error boot initialization: {e}")

init_app_boot_once()

# ---------------------------------------------------------
# PANTALLA DE INICIO DE SESIÓN Y CONTROL DE ACCESO (RBAC)
# ---------------------------------------------------------
if not is_authenticated():
    # CSS MÍNIMO SOLO PARA LOGIN
    st.markdown("""
    <style>
        *, *::before, *::after {
            transition: none !important;
            animation: none !important;
            -webkit-transition: none !important;
            -webkit-animation: none !important;
        }
        .stApp,[data-testid="stMain"]{background:#090a0f!important;}
        section[data-testid="stSidebar"],
        div[data-testid="stSidebarCollapsedControl"],
        header[data-testid="stHeader"],div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],div[data-testid="stToolbar"],
        iframe,#MainMenu,footer,.stDeployButton{display:none!important;}
        [data-testid="stMainBlockContainer"]{
            max-width:460px!important;margin:0 auto!important;padding-top:2.5rem!important;
        }
        /* OCULTAR DEFINITIVAMENTE 'Press Enter to submit form' */
        [data-testid="stInputInstructions"],
        [data-testid="InputInstructions"],
        .stInputInstructions,
        div[data-testid="stForm"] small,
        div[data-testid="stTextInput"] small,
        div[data-baseweb="input"] small {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0px !important;
            width: 0px !important;
            overflow: hidden !important;
            font-size: 0px !important;
            line-height: 0 !important;
        }
        div[data-testid="stForm"]{
            background:#0d0f17;border:1px solid #1c1e29;
            border-radius:12px;padding:24px;
            box-shadow:0 10px 30px rgba(0,0,0,0.6);
        }
        div[data-testid="stFormSubmitButton"] button{
            background:linear-gradient(135deg,#c58b4e,#dfa86a)!important;
            color:#fff!important;font-weight:800!important;
            border:none!important;border-radius:8px!important;
            height:46px!important;font-size:1rem!important;
        }
        div[data-testid="stTextInput"] label{color:#94a3b8!important;font-size:.9rem!important;margin-bottom:4px!important;}
        
        /* UN SOLO CAJÓN LIMPIO Y UNIFICADO PARA ENTRADAS DE TEXTO EN LOGIN */
        div[data-testid="stTextInput"] > div[data-baseweb="input"] {
            background-color: #11131c !important;
            background: #11131c !important;
            border: 1.5px solid #2a2d3e !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            outline: none !important;
            padding: 0 4px !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stTextInput"] > div[data-baseweb="input"]:focus-within,
        div[data-testid="stTextInput"] > div[data-baseweb="input"]:hover {
            border-color: #dfa86a !important;
            box-shadow: 0 0 12px rgba(223, 168, 106, 0.5) !important;
        }
        div[data-testid="stTextInput"] input {
            background: transparent !important;
            background-color: transparent !important;
            color: #ffffff !important;
            border: none !important;
            border-width: 0px !important;
            outline: none !important;
            box-shadow: none !important;
        }
        div[data-testid="stTextInput"] input:focus {
            background: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    logo_b64 = get_logo_base64()
    st.markdown(f'''
    <div style="text-align: center; padding-bottom: 20px; width: 100%;">
        {f'<img src="data:image/png;base64,{logo_b64}" style="height:90px; margin-bottom:10px;"><br>' if logo_b64 else ''}
        <h2 style="color:#dfa86a; margin:0; font-weight:800; letter-spacing:1.5px; font-family:\'Outfit\', sans-serif;">GZG MINERALES PERU S.R.L.</h2>
        <p style="color:#94a3b8; font-size:0.95rem; margin-top:4px;">Sistema de Control de Asistencia y Gestión de Personal</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
    <div style="background: #10131d; border: 1px solid #dfa86a; border-radius: 12px; padding: 18px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; margin-bottom: 20px; width: 100%;">
        <h3 style="color:#ffffff; margin:0; font-family:\'Outfit\', sans-serif;">🔐 Acceso al Sistema</h3>
    </div>
    ''', unsafe_allow_html=True)

    # Formulario de login con soporte Enter key
    with st.form("gzg_login_form", clear_on_submit=False, enter_to_submit=True):
        u_val = st.text_input("Usuario", value="", key="login_u_k",
                              placeholder="Ingrese su usuario...")
        p_val = st.text_input("Contraseña", value="", type="password", key="login_p_k",
                              placeholder="Ingrese su contraseña...",
                              autocomplete="current-password")
        st.markdown("<br>", unsafe_allow_html=True)
        btn_login = st.form_submit_button(
            "🚀 INGRESAR AL SISTEMA",
            use_container_width=True,
            type="primary"
        )

    if btn_login:
        u_s = u_val.strip() if u_val else ""
        p_s = p_val.strip() if p_val else ""
        if u_s and p_s:
            if login_user(u_s, p_s):
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")
        else:
            st.warning("⚠️ Ingrese su usuario y contraseña.")
    st.stop()
current_user = get_current_user()

# Inyectar CSS completo del dashboard SOLO cuando ya está autenticado
_inject_dashboard_css()

logo_b64 = get_logo_base64()
peru_tz = timezone(timedelta(hours=-5))
curr_now = datetime.now(peru_tz)
date_display = curr_now.strftime("%d/%m/%Y")
time_display = curr_now.strftime("%I:%M:%S %p").lower()

if 'last_data_update' not in st.session_state:
    st.session_state['last_data_update'] = time_display
last_update_display = st.session_state['last_data_update']

st.markdown(f'''
<div class="main-header-cajon">
    <div class="header-left">
        <img src="data:image/png;base64,{logo_b64}" class="header-logo" alt="GZG Emblem" />
        <div class="brand-block">
            <div class="brand-gzg">GZG</div>
            <div class="brand-minerales">MINERALES</div>
        </div>
        <div class="header-divider"></div>
        <div class="header-titles">
            <div class="main-title-text">CENTRO DE CONTROL DE ASISTENCIA v1.0</div>
        </div>
    </div>
    <div class="header-widgets">
        <div class="widget-box-equal">
            <div class="widget-label">FECHA</div>
            <div class="widget-val" id="gzg-live-date">{date_display}</div>
        </div>
        <div class="widget-box-equal">
            <div class="widget-label">HORA ACTUAL</div>
            <div class="widget-val" id="gzg-live-clock">{time_display}</div>
        </div>
        <div class="widget-box-equal">
            <div class="widget-label">ÚLTIMA ACTUALIZACIÓN</div>
            <div class="widget-val" id="gzg-last-update">{last_update_display}</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

components.html("""
<script>
    const updateHeaderClock = () => {
        try {
            const pDoc = window.parent.document;
            const elClock = pDoc.getElementById('gzg-live-clock');
            const elDate = pDoc.getElementById('gzg-live-date');
            if (elClock || elDate) {
                const now = new Date();
                const optionsTime = { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
                const optionsDate = { timeZone: 'America/Lima', day: '2-digit', month: '2-digit', year: 'numeric' };
                if (elClock) elClock.textContent = now.toLocaleTimeString('en-US', optionsTime).toLowerCase();
                if (elDate) elDate.textContent = now.toLocaleDateString('es-PE', optionsDate);
            }
        } catch(e){}
    };
    setInterval(updateHeaderClock, 200);
    updateHeaderClock();
</script>
""", height=0, width=0)

DEFAULT_ASISTENCIA_DIR = r"C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\descargas_biometrico"
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "descargas_biometrico"), exist_ok=True)
BASE_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sistema_Asistencia_GZG_v1.0.xlsm")

# Cargar la lista completa de trabajadores desde la BD SQLite
df_trab_master_db, _, df_asis_master_db, _, _ = obtener_datos_db()

# Sidebar Controls
st.sidebar.title("🎛️ PANEL DE CONTROL")

# BADGE DE USUARIO AUTENTICADO
if current_user:
    st.sidebar.markdown(f'''
    <div style="background: rgba(223, 168, 106, 0.08); border: 1px solid #dfa86a; border-radius: 8px; padding: 10px; margin-bottom: 12px;">
        <div style="font-size:0.75rem; color:#a0aab8; font-weight:600;">USUARIO AUTENTICADO</div>
        <div style="font-size:0.95rem; color:#dfa86a; font-weight:700;">{current_user['nombre_completo']}</div>
        <div style="font-size:0.8rem; color:#ffffff; margin-top:2px;">Rol: <b>{current_user['rol']}</b></div>
        <div style="font-size:0.8rem; color:#ffffff;">Área: <b>{current_user['area_asignada']}</b></div>
    </div>
    ''', unsafe_allow_html=True)

    def cb_logout():
        logout_user()

    st.sidebar.button("🔴 CERRAR SESIÓN", use_container_width=True, key="btn_logout_user", on_click=cb_logout)

# 1. SELECTOR DE PERSONAL (FILTRO POR MÚLTIPLES CARGOS Y TRABAJADOR)
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Selector de Personal")

opciones_cargos = []
if not df_trab_master_db.empty and 'CARGO' in df_trab_master_db.columns:
    cargos_raw = df_trab_master_db['CARGO'].dropna().unique()
    cargos_clean = sorted([str(c).strip() for c in cargos_raw if str(c).strip() and str(c).lower() not in ['none', 'n/a', 'nan', '']])
    opciones_cargos = cargos_clean

def cb_select_all_cargos():
    for c in opciones_cargos:
        st.session_state[f"cargo_chk_{c}"] = True

def cb_deselect_all_cargos():
    for c in opciones_cargos:
        st.session_state[f"cargo_chk_{c}"] = False

for c in opciones_cargos:
    if f"cargo_chk_{c}" not in st.session_state:
        st.session_state[f"cargo_chk_{c}"] = True

# Evaluar pre-render de los cargos seleccionados
selected_cargos_pre = [c for c in opciones_cargos if st.session_state.get(f"cargo_chk_{c}", True)]

if len(selected_cargos_pre) == len(opciones_cargos):
    titulo_cargos = "TODOS LOS CARGOS"
elif len(selected_cargos_pre) == 0:
    titulo_cargos = "NINGÚN CARGO SELECCIONADO"
elif len(selected_cargos_pre) <= 2:
    titulo_cargos = ", ".join(selected_cargos_pre)
else:
    titulo_cargos = f"{len(selected_cargos_pre)} Cargos seleccionados"

st.sidebar.markdown("<p class='sidebar-field-title' style='margin-bottom:4px; font-size:0.95rem; font-weight:700; color:#ffffff;'>Filtrar por Cargo(s)</p>", unsafe_allow_html=True)

with st.sidebar.popover(titulo_cargos, use_container_width=True):
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.button("✅ Todos", use_container_width=True, key="btn_select_all_cargos", on_click=cb_select_all_cargos)
    with col_t2:
        st.button("🧹 Desmarcar", use_container_width=True, key="btn_deselect_all_cargos", on_click=cb_deselect_all_cargos)

    st.markdown("<hr style='margin:6px 0; border-top:1px solid #222638;'>", unsafe_allow_html=True)
    
    for cargo_item in opciones_cargos:
        st.checkbox(cargo_item, value=st.session_state.get(f"cargo_chk_{cargo_item}", True), key=f"cargo_chk_{cargo_item}")

# Inicialización de filtros aplicados (SOLO se actualizan tras presionar [🔍 FILTRAR])
if 'applied_cargos' not in st.session_state or st.session_state['applied_cargos'] is None:
    st.session_state['applied_cargos'] = list(opciones_cargos)
if 'applied_worker' not in st.session_state:
    st.session_state['applied_worker'] = "TODO EL PERSONAL"
if 'applied_f_ini' not in st.session_state:
    st.session_state['applied_f_ini'] = date(2026, 8, 1)
if 'applied_f_fin' not in st.session_state:
    st.session_state['applied_f_fin'] = date(2026, 8, 11)

# Lista de cargos que están actualmente marcados en la interfaz
cargos_marcados_ui = [c for c in opciones_cargos if st.session_state.get(f"cargo_chk_{c}", True)]

# Filtrar trabajadores disponibles en el selector según los cargos seleccionados en la UI
df_trab_opciones = df_trab_master_db.copy()
if not df_trab_opciones.empty and 'CARGO' in df_trab_opciones.columns:
    if len(cargos_marcados_ui) == 0:
        df_trab_opciones = df_trab_opciones.iloc[0:0]
    else:
        cargos_ui_upper = {str(c).strip().upper() for c in cargos_marcados_ui}
        df_trab_opciones = df_trab_opciones[df_trab_opciones['CARGO'].astype(str).str.strip().str.upper().isin(cargos_ui_upper)]

opciones_trabajadores = ["TODO EL PERSONAL"]
worker_options_map = {"TODO EL PERSONAL": "TODOS"}

if not df_trab_opciones.empty:
    for _, r in df_trab_opciones.iterrows():
        dni = str(r.get('DNI', '')).strip()
        ape = str(r.get('APELLIDOS', '')).strip()
        nom = str(r.get('NOMBRES', '')).strip()
        if dni and (ape or nom):
            disp = f"{dni} - {ape} {nom}".strip()
            worker_options_map[disp] = dni
            opciones_trabajadores.append(disp)

opciones_trabajadores = ["TODO EL PERSONAL"] + sorted(list(set(opciones_trabajadores[1:])))

# Callback para selección instantánea de trabajador a UN SOLO CLICK
def cb_set_worker(target_val):
    st.session_state['pending_worker_val'] = target_val

worker_actual = st.session_state.get('pending_worker_val', st.session_state.get('applied_worker', 'TODO EL PERSONAL'))
if worker_actual not in opciones_trabajadores:
    worker_actual = 'TODO EL PERSONAL'

st.sidebar.markdown("<p class='sidebar-field-title' style='margin-bottom:4px; margin-top:10px; font-size:0.95rem; font-weight:700; color:#ffffff;'>Filtrar por Trabajador</p>", unsafe_allow_html=True)

# Popover idéntico al de cargos (Selección a UN SOLO CLICK)
if worker_actual == 'TODO EL PERSONAL':
    titulo_trabajador = "TODO EL PERSONAL"
else:
    # mostrar solo apellidos+nombres sin el DNI para titulo corto
    partes = worker_actual.split(' - ', 1)
    titulo_trabajador = partes[1] if len(partes) > 1 else worker_actual
    if len(titulo_trabajador) > 28:
        titulo_trabajador = titulo_trabajador[:26] + "..."

with st.sidebar.popover(titulo_trabajador, use_container_width=True):
    st.button("👥 Todo el Personal", use_container_width=True, key="btn_worker_todos",
              on_click=cb_set_worker, args=("TODO EL PERSONAL",))
    st.markdown("<hr style='margin:6px 0; border-top:1px solid #222638;'>", unsafe_allow_html=True)
    for idx_w, opcion_w in enumerate(opciones_trabajadores[1:]):  # saltar 'TODO EL PERSONAL'
        is_sel = (opcion_w == worker_actual)
        btn_label = ("✅ " if is_sel else "👤 ") + opcion_w
        st.button(btn_label, use_container_width=True, key=f"btn_w_{idx_w}",
                  on_click=cb_set_worker, args=(opcion_w,))

trabajador_seleccionado = st.session_state.get('pending_worker_val', 'TODO EL PERSONAL')
if trabajador_seleccionado not in opciones_trabajadores:
    trabajador_seleccionado = 'TODO EL PERSONAL'

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Consulta por Rango de Fechas")
col_d1, col_d2 = st.sidebar.columns(2)
with col_d1:
    fecha_inicio_sel = st.date_input("Fecha Inicio", value=st.session_state.get('pending_f_ini', st.session_state['applied_f_ini']), key="sidebar_f_ini")
    st.session_state['pending_f_ini'] = fecha_inicio_sel
with col_d2:
    fecha_fin_sel = st.date_input("Fecha Fin", value=st.session_state.get('pending_f_fin', st.session_state['applied_f_fin']), key="sidebar_f_fin")
    st.session_state['pending_f_fin'] = fecha_fin_sel

st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("🔍 FILTRAR", use_container_width=True, type="primary", key="btn_apply_filters"):
    st.session_state['applied_cargos'] = list(cargos_marcados_ui)
    st.session_state['applied_worker'] = trabajador_seleccionado
    st.session_state['applied_f_ini'] = fecha_inicio_sel
    st.session_state['applied_f_fin'] = fecha_fin_sel
    st.session_state['last_data_update'] = datetime.now(peru_tz).strftime("%I:%M:%S %p").lower()
    obtener_datos_db.clear()
    st.toast("🎯 Filtros y KPIs actualizados", icon="🔍")
    st.rerun()



# CARGAR DATOS DE LA BASE DE DATOS SEGÚN RANGO DE FECHAS APLICADO
f_ini_str = st.session_state['applied_f_ini'].strftime("%Y-%m-%d")
f_fin_str = st.session_state['applied_f_fin'].strftime("%Y-%m-%d")

df_trab_db, df_marc_db, df_asis_db, df_he_db, df_inc_db = obtener_datos_db(f_ini_str, f_fin_str)

confirmed_worker = st.session_state['applied_worker']
confirmed_cargos = st.session_state['applied_cargos']
cargos_norm_set = {str(c).strip().upper() for c in confirmed_cargos if str(c).strip()}

# APLICAR FILTRO POR TRABAJADOR O MÚLTIPLES CARGOS CONFIRMADOS
if confirmed_worker in worker_options_map and worker_options_map[confirmed_worker] != "TODOS":
    selected_dni = str(worker_options_map[confirmed_worker]).strip()
    if not df_trab_db.empty and 'DNI' in df_trab_db.columns:
        df_trab_db = df_trab_db[df_trab_db['DNI'].astype(str).str.strip() == selected_dni]
    if not df_asis_db.empty and 'DNI' in df_asis_db.columns:
        df_asis_db = df_asis_db[df_asis_db['DNI'].astype(str).str.strip() == selected_dni]
    if not df_inc_db.empty and 'DNI' in df_inc_db.columns:
        df_inc_db = df_inc_db[df_inc_db['DNI'].astype(str).str.strip() == selected_dni]
    if not df_he_db.empty and 'DNI' in df_he_db.columns:
        df_he_db = df_he_db[df_he_db['DNI'].astype(str).str.strip() == selected_dni]
    if not df_marc_db.empty:
        col_dni = 'ID' if 'ID' in df_marc_db.columns else ('DNI' if 'DNI' in df_marc_db.columns else None)
        if col_dni:
            df_marc_db = df_marc_db[df_marc_db[col_dni].astype(str).str.strip() == selected_dni]

elif len(cargos_norm_set) == 0:
    df_trab_db = df_trab_db.iloc[0:0]
    df_asis_db = df_asis_db.iloc[0:0]
    df_inc_db = df_inc_db.iloc[0:0]
    df_he_db = df_he_db.iloc[0:0]
    df_marc_db = df_marc_db.iloc[0:0]

elif len(cargos_norm_set) < len(opciones_cargos):
    if not df_trab_db.empty and 'CARGO' in df_trab_db.columns:
        df_trab_db = df_trab_db[df_trab_db['CARGO'].astype(str).str.strip().str.upper().isin(cargos_norm_set)]
    if not df_asis_db.empty and 'CARGO' in df_asis_db.columns:
        df_asis_db = df_asis_db[df_asis_db['CARGO'].astype(str).str.strip().str.upper().isin(cargos_norm_set)]
    if not df_inc_db.empty and 'CARGO' in df_inc_db.columns:
        df_inc_db = df_inc_db[df_inc_db['CARGO'].astype(str).str.strip().str.upper().isin(cargos_norm_set)]
    if not df_he_db.empty and 'CARGO' in df_he_db.columns:
        df_he_db = df_he_db[df_he_db['CARGO'].astype(str).str.strip().str.upper().isin(cargos_norm_set)]
    if not df_marc_db.empty and not df_trab_db.empty:
        valid_dnis = set(df_trab_db['DNI'].astype(str).str.strip())
        col_dni = 'ID' if 'ID' in df_marc_db.columns else ('DNI' if 'DNI' in df_marc_db.columns else None)
        if col_dni:
            df_marc_db = df_marc_db[df_marc_db[col_dni].astype(str).str.strip().isin(valid_dnis)]

# APLICACIÓN DE RESTRICCIÓN POR ÁREA ASIGNADA AL USUARIO (RBAC)
if current_user and current_user.get('area_asignada', 'TODAS') != 'TODAS' and current_user['rol'] == 'JEFE_SUPERVISOR':
    user_area = current_user['area_asignada']
    if not df_trab_db.empty:
        col_a = 'AREA' if 'AREA' in df_trab_db.columns else ('ÁREA' if 'ÁREA' in df_trab_db.columns else None)
        if col_a:
            df_trab_db = df_trab_db[df_trab_db[col_a].astype(str).str.strip() == user_area]
    if not df_asis_db.empty:
        col_a = 'ÁREA' if 'ÁREA' in df_asis_db.columns else ('AREA' if 'AREA' in df_asis_db.columns else None)
        if col_a:
            df_asis_db = df_asis_db[df_asis_db[col_a].astype(str).str.strip() == user_area]
    if not df_he_db.empty:
        col_a = 'ÁREA' if 'ÁREA' in df_he_db.columns else ('AREA' if 'AREA' in df_he_db.columns else None)
        if col_a:
            df_he_db = df_he_db[df_he_db[col_a].astype(str).str.strip() == user_area]
    if not df_inc_db.empty:
        col_a = 'ÁREA' if 'ÁREA' in df_inc_db.columns else ('AREA' if 'AREA' in df_inc_db.columns else None)
        if col_a:
            df_inc_db = df_inc_db[df_inc_db[col_a].astype(str).str.strip() == user_area]

col_dl, col_inf = st.columns([1.5, 2.5])

with col_dl:
    if not df_asis_db.empty:
        excel_bytes = exportar_asistencia_excel(
            df_trab_db, df_marc_db, df_asis_db, df_he_db, df_inc_db, BASE_EXCEL
        )
        st.download_button(
            label="📊 DESCARGAR EXCEL BASE v1.0 (.xlsx)",
            data=excel_bytes,
            file_name=f"Sistema_Asistencia_GZG_{f_ini_str}_a_{f_fin_str}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with col_inf:
    st.info(f"📁 Filtro ({f_ini_str} al {f_fin_str}): **{len(df_trab_db)} Personal**, **{len(df_marc_db)} Marcaciones**, **{len(df_asis_db)} Registros Asistencia**")

st.markdown("---")

# NAVEGACIÓN PRINCIPAL POR SECCIONES Y PESTAÑAS (ST.TABS)
opciones_pestanas = [
    "📊 Dashboard Analítico",
    "✅ Bandeja de Aprobaciones (HE / Incidencias)"
]
if current_user and current_user.get('rol') == 'ADMINISTRACION':
    opciones_pestanas.append("👥 Gestión de Usuarios")

pestanas_objs = st.tabs(opciones_pestanas)
tab_dash = pestanas_objs[0]
tab_bandeja = pestanas_objs[1]
tab_usuarios = pestanas_objs[2] if len(pestanas_objs) > 2 else None

# PESTAÑA 1: DASHBOARD ANALÍTICO
with tab_dash:
    if not df_asis_db.empty:
        tot_personal = len(df_trab_db)
        
        total_presentes = len(df_asis_db[df_asis_db['ESTADO ASISTENCIA'] != 'FALTA'])
        total_ausentes = len(df_asis_db[df_asis_db['ESTADO ASISTENCIA'] == 'FALTA'])
            
        tard_num_series = to_numeric_minutes(df_asis_db['TARDANZA (MIN)']) if 'TARDANZA (MIN)' in df_asis_db.columns else pd.Series(0, index=df_asis_db.index)
        total_tardanzas = int((tard_num_series > 0).sum())
        
        exceso_num_series = to_numeric_minutes(df_asis_db['EXCESO JORNADA']) if 'EXCESO JORNADA' in df_asis_db.columns else pd.Series(0, index=df_asis_db.index)
        exceso_jornada_min = int(exceso_num_series.sum())
        exceso_fmt = format_hhmm(exceso_jornada_min)
        
        he_programadas_min = 0
        if not df_he_db.empty and ('DURACIÓN' in df_he_db.columns or 'DURACIÓN (HH:MM)' in df_he_db.columns):
            col_he_target = 'DURACIÓN' if 'DURACIÓN' in df_he_db.columns else 'DURACIÓN (HH:MM)'
            he_programadas_min = int(to_numeric_minutes(df_he_db[col_he_target]).sum())
        he_fmt = format_hhmm(he_programadas_min)
        
        total_incidencias = len(df_asis_db[df_asis_db['ESTADO ASISTENCIA'] == 'ASISTIO CON INCIDENCIAS'])
        
        sal_ant_num_series = to_numeric_minutes(df_asis_db['SALIDA ANTICIPADA (MIN)']) if 'SALIDA ANTICIPADA (MIN)' in df_asis_db.columns else pd.Series(0, index=df_asis_db.index)
        total_salidas_ant = int((sal_ant_num_series > 0).sum())

        pct_asis = round((total_presentes / tot_personal * 100.0) if tot_personal > 0 else 0.0, 1)
        pct_aus = round((total_ausentes / tot_personal * 100.0) if tot_personal > 0 else 0.0, 1)

        tard_mins_series = to_numeric_minutes(df_asis_db['TARDANZA (MIN)']) if 'TARDANZA (MIN)' in df_asis_db.columns else pd.Series(0, index=df_asis_db.index)
        tard_only = tard_mins_series[tard_mins_series > 0]
        prom_tard_min = int(round(tard_only.mean())) if not tard_only.empty else 0
        prom_tard_str = f"Prom. Tardanza: {prom_tard_min} min" if prom_tard_min > 0 else "Total tardanzas"

        # FILA 1: 8 TARJETAS KPI EN UN SOLO RENDER ATÓMICO INSTANTÁNEO
        st.markdown(f'''
        <div class="kpi-grid-container">
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">PERSONAL TOTAL</div>
                    <div class="kpi-cajon-single-number">{tot_personal}</div>
                </div>
            </div>
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(34, 197, 94, 0.15); color: #22c55e;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">PRESENTES</div>
                    <div class="kpi-cajon-single-number">{total_presentes}</div>
                </div>
            </div>
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(148, 163, 184, 0.15); color: #94a3b8;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">AUSENTES</div>
                    <div class="kpi-cajon-single-number">{total_ausentes}</div>
                </div>
            </div>
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">TARDANZAS</div>
                    <div class="kpi-cajon-single-number">{total_tardanzas}</div>
                </div>
            </div>
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(168, 85, 247, 0.15); color: #a855f7;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42C17.99 7.86 19 9.81 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-2.19 1.01-4.14 2.58-5.42L6.17 5.17C4.23 6.82 3 9.26 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">EXCESO JORNADA</div>
                    <div class="kpi-cajon-single-number">{exceso_fmt}</div>
                </div>
            </div>
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">HORAS EXTRA H.E.</div>
                    <div class="kpi-cajon-single-number">{he_fmt}</div>
                </div>
            </div>
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(239, 68, 68, 0.15); color: #ef4444;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">INCIDENCIAS</div>
                    <div class="kpi-cajon-single-number">{total_incidencias}</div>
                </div>
            </div>
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(236, 72, 153, 0.15); color: #ec4899;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">SALIDAS ANTICIPADAS</div>
                    <div class="kpi-cajon-single-number">{total_salidas_ant}</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        COLOR_MAP_ESTADOS = {
            'ASISTIO': '#22c55e',
            'ASISTIO CON H.E.': '#3b82f6',
            'TARDANZA': '#f59e0b',
            'SALIDA ANTICIPADA': '#ec4899',
            'TARDANZA + SALIDA ANTICIPADA': '#d946ef',
            'ASISTIO CON INCIDENCIAS': '#ef4444',
            'SALIDA PENDIENTE': '#eab308',
            'ENTRADA PENDIENTE': '#f97316',
            'FALTA': '#64748b'
        }

        # FILA 2: DONUT CHART Y BAR CHART POR CARGO
        c_chart1, c_chart2 = st.columns([1, 2])
        
        with c_chart1:
            st.markdown('<div class="section-title">📊 Distribución de Estados de Asistencia</div>', unsafe_allow_html=True)
            estado_counts = df_asis_db['ESTADO ASISTENCIA'].value_counts().reset_index()
            estado_counts.columns = ['Estado', 'Cantidad']
            total_reg = int(estado_counts['Cantidad'].sum())
            
            legend_labels = []
            colors_list = []
            for _, r in estado_counts.iterrows():
                est = str(r['Estado'])
                cnt = int(r['Cantidad'])
                pct = (cnt / total_reg * 100.0) if total_reg > 0 else 0.0
                lbl = f"{est}<br><b>{cnt:,}</b> ({pct:.1f}%)"
                legend_labels.append(lbl)
                colors_list.append(COLOR_MAP_ESTADOS.get(est, '#3b82f6'))

            fig_donut_est = go.Figure(data=[go.Pie(
                labels=legend_labels,
                values=estado_counts['Cantidad'],
                hole=0.55,
                marker=dict(colors=colors_list, line=dict(color='#0e1017', width=2)),
                textinfo='percent',
                texttemplate='%{percent:.1%}',
                textfont=dict(color='#ffffff', size=14, family='Segoe UI, sans-serif'),
                sort=False,
                direction='clockwise'
            )])

            fig_donut_est.update_layout(
                paper_bgcolor='#090a0f', plot_bgcolor='#090a0f',
                font=dict(color='#ffffff', size=14, family='Segoe UI, sans-serif'),
                showlegend=True,
                legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center", bgcolor="#090a0f", font=dict(color='#ffffff', size=14, family='Segoe UI, sans-serif')),
                annotations=[dict(text="<b style='letter-spacing: 2px;'>TOTAL</b>", x=0.5, y=0.56, font=dict(color='#94a3b8', size=11, family='Segoe UI, sans-serif'), showarrow=False),
                             dict(text=f"<b style='font-size: 26px; color: #ffffff;'>{total_reg:,}</b>", x=0.5, y=0.44, font=dict(color='#ffffff', size=26, family='Segoe UI, sans-serif'), showarrow=False)],
                margin=dict(t=20, b=90, l=20, r=20), height=460
            )
            st.plotly_chart(fig_donut_est, use_container_width=True, config={'responsive': True})

        with c_chart2:
            st.markdown('<div class="section-title">📈 Registros de Asistencia por Cargo</div>', unsafe_allow_html=True)
            if 'CARGO' in df_asis_db.columns:
                cargo_counts = df_asis_db.groupby(['CARGO', 'ESTADO ASISTENCIA']).size().reset_index(name='Cantidad')
                cargo_totals = df_asis_db.groupby('CARGO').size().reset_index(name='Total')

                fig_bar = px.bar(
                    cargo_counts, x='CARGO', y='Cantidad', color='ESTADO ASISTENCIA',
                    color_discrete_map=COLOR_MAP_ESTADOS, barmode='stack', text='Cantidad', height=460
                )
                fig_bar.update_traces(
                    textposition='inside',
                    insidetextanchor='middle',
                    textfont=dict(color='#ffffff', size=12, family='Segoe UI, sans-serif'),
                    hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y}<extra></extra>"
                )

                # AÑADIR TOTAL GENERAL EN LA PARTE SUPERIOR DE CADA BARRA DE FORMA ELEGANTE
                fig_bar.add_trace(go.Scatter(
                    x=cargo_totals['CARGO'],
                    y=cargo_totals['Total'],
                    text=cargo_totals['Total'].apply(lambda v: f"<b>{v}</b>"),
                    mode='text',
                    textposition='top center',
                    textfont=dict(color='#ffffff', size=13, family='Segoe UI, sans-serif'),
                    showlegend=False,
                    hoverinfo='skip'
                ))

                max_total = int(cargo_totals['Total'].max()) if not cargo_totals.empty else 10
                y_max = int(max_total * 1.15) + 1

                fig_bar.update_layout(
                    paper_bgcolor='#090a0f', plot_bgcolor='#090a0f',
                    font=dict(color='#ffffff', size=13, family='Segoe UI, sans-serif'),
                    xaxis=dict(title=dict(text='Cargo', font=dict(color='#ffffff', size=14)), tickfont=dict(color='#ffffff', size=12), showgrid=False),
                    yaxis=dict(title=dict(text='Cantidad de Registros', font=dict(color='#ffffff', size=14)), range=[0, y_max], tickfont=dict(color='#ffffff', size=12), showgrid=True, gridcolor='#1c1e29'),
                    legend=dict(orientation="h", y=-0.28, x=0.5, xanchor="center", bgcolor="#090a0f", font=dict(color='#ffffff', size=13, family='Segoe UI, sans-serif')),
                    margin=dict(t=30, b=90, l=10, r=10)
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={'responsive': True})

        # FILA 3: TENDENCIA DIARIA DE ASISTENCIA Y DISTRIBUCIÓN DE HORAS EXTRA POR ÁREA
        st.markdown("<br>", unsafe_allow_html=True)
        c_tr1, c_tr2 = st.columns([1.5, 1])

        with c_tr1:
            st.markdown('<div class="section-title">📈 Tendencia Diaria de Asistencias, Tardanzas e Incidencias</div>', unsafe_allow_html=True)
            if 'FECHA' in df_asis_db.columns:
                df_trend = df_asis_db.groupby('FECHA').agg(
                    Asistencias=('ESTADO ASISTENCIA', lambda x: (x != 'FALTA').sum()),
                    Tardanzas=('TARDANZA (MIN)', lambda x: (to_numeric_minutes(x) > 0).sum()),
                    Incidencias=('ESTADO ASISTENCIA', lambda x: (x == 'ASISTIO CON INCIDENCIAS').sum())
                ).reset_index()

                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(x=df_trend['FECHA'], y=df_trend['Asistencias'], name='Asistencias', mode='lines+markers', line=dict(color='#22c55e', width=3)))
                fig_line.add_trace(go.Scatter(x=df_trend['FECHA'], y=df_trend['Tardanzas'], name='Tardanzas', mode='lines+markers', line=dict(color='#f59e0b', width=2.5)))
                fig_line.add_trace(go.Scatter(x=df_trend['FECHA'], y=df_trend['Incidencias'], name='Incidencias', mode='lines+markers', line=dict(color='#ef4444', width=2.5)))

                fig_line.update_layout(
                    paper_bgcolor='#090a0f', plot_bgcolor='#090a0f',
                    font=dict(color='#ffffff', size=13, family='Segoe UI, sans-serif'),
                    xaxis=dict(title='Fecha', showgrid=False, tickfont=dict(color='#ffffff')),
                    yaxis=dict(title='Cantidad de Personal', showgrid=True, gridcolor='#1c1e29', tickfont=dict(color='#ffffff')),
                    legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center", bgcolor="#090a0f"),
                    margin=dict(t=20, b=60, l=10, r=10), height=380
                )
                st.plotly_chart(fig_line, use_container_width=True, config={'responsive': True})

        with c_tr2:
            st.markdown('<div class="section-title">📊 Horas Extra Acumuladas por Área</div>', unsafe_allow_html=True)
            if not df_he_db.empty and ('ÁREA' in df_he_db.columns or 'AREA' in df_he_db.columns):
                col_area_he = 'ÁREA' if 'ÁREA' in df_he_db.columns else 'AREA'
                col_he_target = 'DURACIÓN' if 'DURACIÓN' in df_he_db.columns else 'DURACIÓN (HH:MM)'
                df_he_area = df_he_db.copy()
                df_he_area['MINUTOS'] = to_numeric_minutes(df_he_area[col_he_target])
                df_he_grouped = df_he_area.groupby(col_area_he)['MINUTOS'].sum().reset_index()
                df_he_grouped['HH:MM'] = df_he_grouped['MINUTOS'].apply(format_hhmm)
                df_he_grouped = df_he_grouped.sort_values(by='MINUTOS', ascending=True)

                fig_he_bar = px.bar(
                    df_he_grouped, y=col_area_he, x='MINUTOS', orientation='h',
                    text='HH:MM', color_discrete_sequence=['#3b82f6'], height=380
                )
                fig_he_bar.update_traces(textposition='outside', textfont=dict(color='#ffffff', size=12, weight='bold'))
                fig_he_bar.update_layout(
                    paper_bgcolor='#090a0f', plot_bgcolor='#090a0f',
                    font=dict(color='#ffffff', size=13, family='Segoe UI, sans-serif'),
                    xaxis=dict(title='Minutos Acumulados', showgrid=True, gridcolor='#1c1e29', tickfont=dict(color='#ffffff')),
                    yaxis=dict(title='Área', showgrid=False, tickfont=dict(color='#ffffff')),
                    margin=dict(t=20, b=40, l=10, r=10)
                )
                st.plotly_chart(fig_he_bar, use_container_width=True, config={'responsive': True})
            else:
                st.info("Sin registros de Horas Extra para mostrar por área.")

        # FILA 4: RANKINGS TOP 5 EJECUTIVOS
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="color: #ffffff; font-size: 1.45rem; font-weight: 900; margin-top: 0.2rem; margin-bottom: 0.85rem; display: flex; align-items: center; justify-content: flex-start; text-align: left; gap: 8px; padding: 0; margin-left: 0;">🏆 Ranking Top 5</div>', unsafe_allow_html=True)

        col_top1, col_top2, col_top3 = st.columns(3)

        with col_top1:
            st.markdown('''
            <div class="top10-container">
                <div class="top10-title-yellow">⚠️ TOP 5 TARDANZAS</div>
            ''', unsafe_allow_html=True)
            if 'TARDANZA (MIN)' in df_asis_db.columns:
                df_tard_rank = df_asis_db.copy()
                df_tard_rank['MINUTOS'] = to_numeric_minutes(df_tard_rank['TARDANZA (MIN)'])
                df_tard_sum = df_tard_rank.groupby(['DNI', 'APELLIDOS', 'NOMBRES'])['MINUTOS'].sum().reset_index()
                df_tard_sum = df_tard_sum[df_tard_sum['MINUTOS'] > 0].sort_values(by='MINUTOS', ascending=False).head(5)
                
                if not df_tard_sum.empty:
                    rows_html = ""
                    for idx, (_, r) in enumerate(df_tard_sum.iterrows(), start=1):
                        nombre = f"{r['APELLIDOS']} {r['NOMBRES']}".strip()
                        min_str = format_hhmm(r['MINUTOS'])
                        rows_html += f"<tr><td class='top10-num'>{idx}</td><td style='text-align:left;'>{nombre}</td><td>{min_str}</td></tr>"
                    
                    st.markdown(f'''
                    <table class="top10-table-custom">
                        <thead><tr><th>#</th><th style="text-align:left;">Nombre</th><th>HH:MM</th></tr></thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("Sin tardanzas registradas.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_top2:
            st.markdown('''
            <div class="top10-container">
                <div class="top10-title-blue">⏱️ TOP 5 HORAS EXTRA</div>
            ''', unsafe_allow_html=True)
            if not df_he_db.empty:
                col_he_target = 'DURACIÓN' if 'DURACIÓN' in df_he_db.columns else 'DURACIÓN (HH:MM)'
                df_he_rank = df_he_db.copy()
                df_he_rank['MINUTOS'] = to_numeric_minutes(df_he_rank[col_he_target])
                df_he_sum = df_he_rank.groupby(['DNI', 'APELLIDOS', 'NOMBRES'])['MINUTOS'].sum().reset_index()
                df_he_sum = df_he_sum[df_he_sum['MINUTOS'] > 0].sort_values(by='MINUTOS', ascending=False).head(5)
                
                if not df_he_sum.empty:
                    rows_html = ""
                    for idx, (_, r) in enumerate(df_he_sum.iterrows(), start=1):
                        nombre = f"{r['APELLIDOS']} {r['NOMBRES']}".strip()
                        min_str = format_hhmm(r['MINUTOS'])
                        rows_html += f"<tr><td class='top10-num'>{idx}</td><td style='text-align:left;'>{nombre}</td><td>{min_str}</td></tr>"
                    
                    st.markdown(f'''
                    <table class="top10-table-custom">
                        <thead><tr><th>#</th><th style="text-align:left;">Nombre</th><th>HH:MM</th></tr></thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("Sin horas extra registradas.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_top3:
            st.markdown('''
            <div class="top10-container">
                <div class="top10-title-red">🚨 TOP 5 INCIDENCIAS</div>
            ''', unsafe_allow_html=True)
            if not df_inc_db.empty:
                df_inc_rank = df_inc_db.groupby(['DNI', 'APELLIDOS', 'NOMBRES']).size().reset_index(name='CANTIDAD')
                df_inc_rank = df_inc_rank.sort_values(by='CANTIDAD', ascending=False).head(5)
                
                if not df_inc_rank.empty:
                    rows_html = ""
                    for idx, (_, r) in enumerate(df_inc_rank.iterrows(), start=1):
                        nombre = f"{r['APELLIDOS']} {r['NOMBRES']}".strip()
                        rows_html += f"<tr><td class='top10-num'>{idx}</td><td style='text-align:left;'>{nombre}</td><td>{r['CANTIDAD']} reg.</td></tr>"
                    
                    st.markdown(f'''
                    <table class="top10-table-custom">
                        <thead><tr><th>#</th><th style="text-align:left;">Nombre</th><th>Total</th></tr></thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("Sin incidencias registradas.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👋 **Bienvenido al Sistema de Asistencia GZG**. Selecciona o carga un archivo de transacciones Hikvision en el panel izquierdo y presiona **PROCESAR ASISTENCIA** para visualizar los indicadores y guardar en la Base de Datos.")

# PESTAÑA 2: BANDEJA DE APROBACIONES
with tab_bandeja:
    st.subheader("✅ Bandeja de Validación y Aprobación de Jornadas")
    st.markdown("Permite a los Jefes de Área, Superintendencia y Administración autorizar o justificar registros de Horas Extra e Inconsistencias.")
    
    sub_he, sub_inc = st.tabs(["⏱️ Validación de Horas Extra", "🚨 Validación de Incidencias"])
    
    with sub_he:
        st.markdown("### ⏱️ Registros de Horas Extra")
        col_f1, _ = st.columns([1, 2])
        with col_f1:
            estado_he_filter = st.selectbox("Filtrar Estado H.E.", ["PENDIENTE", "APROBADO", "RECHAZADO", "TODOS"], key="val_he_filter")
        
        df_he_val = df_he_db.copy()
        if not df_he_val.empty and 'ESTADO VALIDADOR' in df_he_val.columns:
            if estado_he_filter != "TODOS":
                df_he_val = df_he_val[df_he_val['ESTADO VALIDADOR'] == estado_he_filter]
                
            st.dataframe(df_he_val, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("#### ✍️ Evaluar Registro de Horas Extra")
            
            list_he = df_he_val['ID_REGISTRO'].tolist() if 'ID_REGISTRO' in df_he_val.columns else []
            if list_he:
                selected_he_id = st.selectbox("Seleccionar ID de Registro H.E.", list_he, key="sb_he_id")
                row_he = df_he_val[df_he_val['ID_REGISTRO'] == selected_he_id].iloc[0]
                
                st.info(f"Evaluando a **{row_he.get('NOMBRES', '')} {row_he.get('APELLIDOS', '')}** | DNI: {row_he.get('DNI', '')} | Duración: **{row_he.get('DURACIÓN (HH:MM)', '00:00')}** ({row_he.get('FECHA', '')})")
                
                with st.form("form_val_he"):
                    c_val1, c_val2 = st.columns(2)
                    with c_val1:
                        nuevo_est_he = st.radio("Decisión:", ["APROBADO", "RECHAZADO", "PENDIENTE"], horizontal=True)
                    with c_val2:
                        obs_he = st.text_area("Observación / Justificación", value=str(row_he.get('OBSERVACIÓN VALIDADOR', '')), height=70)
                    
                    btn_save_he = st.form_submit_button("💾 GUARDAR EVALUACIÓN DE H.E.", type="primary")
                    if btn_save_he:
                        actualizar_estado_he(selected_he_id, nuevo_est_he, current_user['username'], obs_he)
                        st.toast(f"✅ Registro #{selected_he_id} marcado como {nuevo_est_he}", icon="💾")
                        st.rerun()
            else:
                st.info("No hay registros de Horas Extra en este filtro.")
        else:
            st.info("Sin registros de Horas Extra para mostrar.")

    with sub_inc:
        st.markdown("### 🚨 Registros de Incidencias e Inconsistencias")
        col_fi1, _ = st.columns([1, 2])
        with col_fi1:
            estado_inc_filter = st.selectbox("Filtrar Estado Incidencias", ["PENDIENTE", "APROBADO", "RECHAZADO", "TODOS"], key="val_inc_filter")
            
        df_inc_val = df_inc_db.copy()
        if not df_inc_val.empty and 'ESTADO VALIDADOR' in df_inc_val.columns:
            if estado_inc_filter != "TODOS":
                df_inc_val = df_inc_val[df_inc_val['ESTADO VALIDADOR'] == estado_inc_filter]
                
            st.dataframe(df_inc_val, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("#### ✍️ Justificar / Evaluar Incidencia")
            
            list_inc = df_inc_val['ID_REGISTRO'].tolist() if 'ID_REGISTRO' in df_inc_val.columns else []
            if list_inc:
                selected_inc_id = st.selectbox("Seleccionar ID de Incidencia", list_inc, key="sb_inc_id")
                row_inc = df_inc_val[df_inc_val['ID_REGISTRO'] == selected_inc_id].iloc[0]
                
                st.warning(f"Evaluando a **{row_inc.get('NOMBRES', '')} {row_inc.get('APELLIDOS', '')}** | Tipo: **{row_inc.get('TIPO', '')}** - {row_inc.get('DESCRIPCIÓN', '')} ({row_inc.get('FECHA', '')})")
                
                with st.form("form_val_inc"):
                    c_vinc1, c_vinc2 = st.columns(2)
                    with c_vinc1:
                        nuevo_est_inc = st.radio("Decisión:", ["APROBADO", "RECHAZADO", "PENDIENTE"], horizontal=True, key="radio_est_inc")
                    with c_vinc2:
                        obs_inc = st.text_area("Justificación u Observación", value=str(row_inc.get('OBSERVACIÓN VALIDADOR', '')), height=70, key="ta_obs_inc")
                    
                    btn_save_inc = st.form_submit_button("💾 GUARDAR EVALUACIÓN DE INCIDENCIA", type="primary")
                    if btn_save_inc:
                        actualizar_estado_incidencia(selected_inc_id, nuevo_est_inc, current_user['username'], obs_inc)
                        st.toast(f"✅ Incidencia #{selected_inc_id} marcada como {nuevo_est_inc}", icon="💾")
                        st.rerun()
            else:
                st.info("No hay incidencias en este filtro.")
        else:
            st.info("Sin incidencias registradas para mostrar.")

# PESTAÑA 3: GESTIÓN DE USUARIOS (SOLO ADMIN)
if tab_usuarios:
    with tab_usuarios:
        st.subheader("👥 Gestión de Usuarios y Roles de Acceso (RBAC)")
        st.markdown("Módulo exclusivo para Administración de Recursos Humanos.")
        
        col_u1, col_u2 = st.columns([1, 1.2])
        
        with col_u1:
            st.markdown("#### ➕ Registrar Nuevo Usuario")
            with st.form("form_nuevo_usuario"):
                u_name = st.text_input("Nombre de Usuario (Username)", placeholder="ej. juan.perez")
                u_nombre = st.text_input("Nombre Completo", placeholder="ej. Ing. Juan Pérez")
                u_pass = st.text_input("Contraseña", type="password")
                u_rol = st.selectbox("Rol de Acceso", ["JEFE_SUPERVISOR", "SUPERINTENDENTE", "GERENTE_PLANTA", "GERENTE_GENERAL", "ADMINISTRACION"])
                u_area = st.selectbox("Área Asignada", ["OPER&MTTO", "JEFATURA", "TODAS"])
                u_cargo = st.text_input("Cargo Oficial", placeholder="ej. Jefe de Mantenimiento")
                
                btn_crear_u = st.form_submit_button("➕ CREAR USUARIO", type="primary", use_container_width=True)
                if btn_crear_u:
                    if u_name and u_pass and u_nombre:
                        pass_h = hash_password(u_pass)
                        res = crear_usuario(u_name, pass_h, u_nombre, u_rol, u_area, u_cargo)
                        if res:
                            st.toast("✅ Usuario creado exitosamente", icon="🎉")
                            st.success(f"Usuario '{u_name}' registrado correctamente.")
                            st.rerun()
                        else:
                            st.error("Error al crear usuario. El username ya podría existir.")
                    else:
                        st.warning("Completa todos los campos obligatorios.")

        with col_u2:
            st.markdown("#### 📜 Usuarios Registrados")
            df_users = obtener_todos_usuarios()
            if not df_users.empty:
                st.dataframe(df_users, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("#### 🗑️ Eliminar Usuario")
                u_del_id = st.selectbox("Seleccionar ID de Usuario a Eliminar", df_users['id'].tolist(), format_func=lambda x: f"ID {x} - {df_users[df_users['id']==x]['username'].values[0]}")
                if st.button("🗑️ Eliminar Usuario Seleccionado"):
                    eliminar_usuario(u_del_id)
                    st.toast("✅ Usuario eliminado correctamente")
                    st.rerun()
