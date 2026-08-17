import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
from datetime import datetime, date
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

# Inicializar Base de Datos y Autenticación RBAC
init_db()
init_auth()

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

# Custom CSS: Theme Negro Absoluto, Bronze Elegante GZG, Ocultar Botones Derechos Superior
st.markdown("""
<style>
    /* Theme Base Oscuro (#090a0f) */
    .stApp, [data-testid="stMain"] {
        background-color: #090a0f !important;
        color: #ffffff;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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

    /* Inputs, Selectbox, Combobox, Date Inputs en Sidebar */
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] div[role="combobox"] {
        color: #ffffff !important;
        background-color: #11131c !important;
        border: 1px solid #222638 !important;
        border-radius: 8px !important;
        font-size: 0.90rem !important;
        font-weight: 700 !important;
        text-align: center !important;
    }

    /* IGUALAR TAMAÑO Y PESO DE FUENTE EXACTOS EN CAJÓN DE TRABAJADOR Y CAJÓN DE CARGOS */
    section[data-testid="stSidebar"] div[data-baseweb="select"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] *,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] p,
    section[data-testid="stSidebar"] div[data-baseweb="select"] input,
    section[data-testid="stSidebar"] div[role="combobox"],
    div[data-testid="stPopover"] > button,
    div[data-testid="stPopover"] > button *,
    div[data-testid="stPopover"] > button p,
    div[data-testid="stPopover"] > button span,
    div[data-testid="stPopover"] > button div {
        font-size: 0.90rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;
        line-height: 1.2 !important;
    }

    /* IGUALAR ALTURA Y ESTILO DE BORDES DE AMBOS BOTONES CAJÓN EN EL SIDEBAR */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    div[data-testid="stPopover"] > button {
        height: 40px !important;
        min-height: 40px !important;
        max-height: 40px !important;
        border-radius: 8px !important;
        background-color: #11131c !important;
        border: 1px solid #222638 !important;
    }

    /* ESTILOS DE SELECTOR DE CARGO LIMPIO (SIN BLOQUE NEGRO NI ETIQUETAS APILADAS) */
    div[data-testid="stPopover"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-top: 2px !important;
    }

    div[data-testid="stPopover"] > button:hover,
    div[data-testid="stPopover"] > button:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.3) !important;
        color: #ffffff !important;
    }

    div[data-testid="stPopover"] > button p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.90rem !important;
        margin: 0 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* ESTILO PARA EL MENÚ DESPLEGABLE CON CHECKMARKS */
    div[data-testid="stPopoverBody"] {
        background-color: #11131c !important;
        background: #11131c !important;
        border: 1.5px solid #c58b4e !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.95) !important;
        padding: 12px !important;
    }

    div[data-testid="stPopoverBody"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    div[data-baseweb="tag"] svg,
    div[data-baseweb="tag"] button {
        fill: #f59e0b !important;
        color: #f59e0b !important;
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

    section[data-testid="stSidebar"] input:focus, 
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

    /* TARJETAS KPI SUPERIORES (TÍTULO Y NÚMERO CENTRADOS EN EL ESPACIO RESTANTE) */
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
        color: #f59e0b;
        font-weight: 900;
        text-align: center !important;
        font-size: 1.15rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ---------------------------------------------------------
# AUTO-SEEDA EN MEMORIA ONCE AT BOOT (RESPUESTA INSTANTÁNEA EN LOGIN)
# ---------------------------------------------------------
@st.cache_resource
def auto_seed_database_if_empty():
    try:
        init_db()
        _, _, df_asis_chk, _, _ = obtener_datos_db()
        if df_asis_chk.empty:
            sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "descargas_biometrico", "Transacciones_2026-08-01_2026-08-11.xlsx")
            if os.path.exists(sample_file):
                df_t_samp, df_m_samp, df_he_samp = cargar_datos_excel(sample_file)
                base_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sistema_Asistencia_GZG_v1.0.xlsm")
                if os.path.exists(base_file):
                    df_t_master, _, _ = cargar_datos_excel(base_file)
                    if df_t_samp.empty:
                        df_t_samp = df_t_master
                guardar_trabajadores(df_t_samp)
                guardar_marcaciones_raw(df_m_samp, archivo_origen=sample_file)
                df_asis_s, df_he_s, df_inc_s, _ = procesar_asistencia_df(df_t_samp, df_m_samp, df_he_samp, AttendanceConfig())
                guardar_asistencia_y_reportes(df_asis_s, df_he_s, df_inc_s)
    except Exception as e:
        print(f"Error auto-seeding: {e}")

# ---------------------------------------------------------
# PANTALLA DE INICIO DE SESIÓN Y CONTROL DE ACCESO (RBAC)
# ---------------------------------------------------------
if not is_authenticated():
    # Procesar intento de login desde parámetros de URL formateados por el formulario HTML nativo
    if "u" in st.query_params and "p" in st.query_params:
        u_q = st.query_params.get("u", "")
        p_q = st.query_params.get("p", "")
        st.query_params.clear()
        if login_user(u_q.strip(), p_q.strip()):
            st.rerun()
        else:
            st.session_state["login_err_msg"] = "❌ Usuario o contraseña incorrectos."

    login_holder = st.empty()
    with login_holder.container():
        st.markdown("""
        <style>
            section[data-testid="stSidebar"],
            div[data-testid="stSidebarCollapsedControl"] {
                display: none !important;
            }
            [data-testid="stMainBlockContainer"] {
                max-width: 460px !important;
                margin: 0 auto !important;
                padding-top: 3.5rem !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        logo_b64 = get_logo_base64()
        st.markdown(f'''
        <div style="text-align: center; padding-bottom: 20px;">
            {f'<img src="data:image/png;base64,{logo_b64}" style="height:90px; margin-bottom:10px;"><br>' if logo_b64 else ''}
            <h2 style="color:#dfa86a; margin:0; font-weight:800; letter-spacing:1.5px; font-family:\'Outfit\', sans-serif;">GZG MINERALES PERU S.R.L.</h2>
            <p style="color:#94a3b8; font-size:0.95rem; margin-top:4px;">Sistema de Control de Asistencia y Gestión de Personal</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div style="background: #10131d; border: 1px solid #dfa86a; border-radius: 12px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; margin-bottom: 20px;">
            <h3 style="color:#ffffff; margin:0; font-family:\'Outfit\', sans-serif;">🔐 Acceso al Sistema</h3>
        </div>
        ''', unsafe_allow_html=True)

        if "login_err_msg" in st.session_state and st.session_state["login_err_msg"]:
            st.error(st.session_state["login_err_msg"])
            st.session_state["login_err_msg"] = None
        
        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', Roboto, sans-serif; color: #ffffff; }
                .form-box { display: flex; flex-direction: column; gap: 14px; }
                .field-group { display: flex; flex-direction: column; gap: 6px; }
                .field-label { color: #ffffff; font-size: 0.95rem; font-weight: 700; }
                .field-input { background: #11131c; border: 1px solid #222638; border-radius: 8px; color: #ffffff; padding: 12px 14px; font-size: 1rem; outline: none; transition: border-color 0.2s, box-shadow 0.2s; box-sizing: border-box; width: 100%; }
                .field-input:focus { border-color: #f59e0b; box-shadow: 0 0 10px rgba(245, 158, 11, 0.3); }
                .submit-btn { margin-top: 8px; background: #0284c7; color: #ffffff; border: 1px solid #0369a1; border-radius: 8px; padding: 13px; font-size: 1rem; font-weight: 800; cursor: pointer; width: 100%; transition: background-color 0.2s, box-shadow 0.2s; }
                .submit-btn:hover { background: #0369a1; box-shadow: 0 0 14px rgba(56, 189, 248, 0.4); }
            </style>
        </head>
        <body>
            <form id="gzg_login_form" class="form-box">
                <div class="field-group">
                    <label class="field-label">Usuario</label>
                    <input type="text" id="gzg_user" autocomplete="off" required class="field-input" />
                </div>
                <div class="field-group">
                    <label class="field-label">Contraseña</label>
                    <input type="password" id="gzg_pass" autocomplete="off" required class="field-input" />
                </div>
                <button type="submit" class="submit-btn">🚀 INGRESAR AL SISTEMA</button>
            </form>
            <script>
                document.getElementById('gzg_login_form').onsubmit = function(e) {
                    e.preventDefault();
                    const u = document.getElementById('gzg_user').value;
                    const p = document.getElementById('gzg_pass').value;
                    if(u && p) {
                        window.parent.location.search = '?u=' + encodeURIComponent(u) + '&p=' + encodeURIComponent(p);
                    }
                };
            </script>
        </body>
        </html>
        """, height=260)
    st.stop()

auto_seed_database_if_empty()
current_user = get_current_user()

logo_b64 = get_logo_base64()
curr_now = datetime.now()
date_display = curr_now.strftime("%d/%m/%Y")
time_display = curr_now.strftime("%I:%M:%S %p").lower()

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
            <div class="widget-val">{date_display}</div>
        </div>
        <div class="widget-box-equal">
            <div class="widget-label">HORA ACTUAL</div>
            <div class="widget-val">{time_display}</div>
        </div>
        <div class="widget-box-equal">
            <div class="widget-label">ÚLTIMA ACTUALIZACIÓN</div>
            <div class="widget-val">{time_display}</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

DEFAULT_ASISTENCIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "descargas_biometrico")
os.makedirs(DEFAULT_ASISTENCIA_DIR, exist_ok=True)
BASE_EXCEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sistema_Asistencia_GZG_v1.0.xlsm")

# Cargar la lista completa de trabajadores desde la BD SQLite
df_trab_master_db, _, df_asis_master_db, _, _ = obtener_datos_db()

worker_options_map = {"TODO EL PERSONAL": "TODOS"}
opciones_cargos = []

if not df_trab_master_db.empty:
    col_c_master = 'CARGO' if 'CARGO' in df_trab_master_db.columns else None
    if col_c_master:
        cargos_raw = df_trab_master_db[col_c_master].dropna().unique()
        cargos_clean = [str(c).strip() for c in cargos_raw if str(c).strip() and str(c).lower() not in ['none', 'n/a', 'nan', '']]
        opciones_cargos = sorted(list(set(cargos_clean)))

# INICIALIZACIÓN DE SESSION STATE PARA BÚSQUEDA Y DASHBOARD
if 'active_cargos' not in st.session_state or not st.session_state['active_cargos']:
    st.session_state['active_cargos'] = opciones_cargos
if 'active_worker' not in st.session_state:
    st.session_state['active_worker'] = "TODO EL PERSONAL"
if 'active_f_ini' not in st.session_state:
    st.session_state['active_f_ini'] = date(2026, 8, 1)
if 'active_f_fin' not in st.session_state:
    st.session_state['active_f_fin'] = date(2026, 8, 11)

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
    if st.sidebar.button("🔴 CERRAR SESIÓN", use_container_width=True):
        logout_user()
        st.toast("👋 Sesión cerrada correctamente")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("👤 Selector de Personal")

# 1. SELECTOR MULTIPLE DE CARGO (CON BOTONES 'TODOS' Y 'DESMARCAR')
for c in opciones_cargos:
    if f"chk_c_{c}" not in st.session_state:
        st.session_state[f"chk_c_{c}"] = True

selected_cargos_keys = [c for c in opciones_cargos if st.session_state.get(f"chk_c_{c}", True)]

if len(selected_cargos_keys) == 0:
    pending_cargos = ["__NINGUNO__"]
else:
    pending_cargos = selected_cargos_keys

if not pending_cargos:
    texto_boton = "TODOS LOS CARGOS (Sin filtro)"
elif pending_cargos == ["__NINGUNO__"]:
    texto_boton = "NINGÚN CARGO SELECCIONADO"
elif len(pending_cargos) <= 2:
    texto_boton = ", ".join(pending_cargos)
else:
    texto_boton = f"{len(pending_cargos)} Cargos seleccionados"

st.sidebar.markdown("<p class='sidebar-field-title' style='margin-bottom:4px; font-size:0.95rem; font-weight:700; color:#ffffff;'>Filtrar por Cargo(s)</p>", unsafe_allow_html=True)

with st.sidebar.popover(texto_boton, use_container_width=True):
    col_all1, col_all2 = st.columns(2)
    with col_all1:
        if st.button("✅ Todos", use_container_width=True, key="pop_btn_marcar_todos"):
            for c in opciones_cargos:
                st.session_state[f"chk_c_{c}"] = True
            st.rerun()
    with col_all2:
        if st.button("🧹 Desmarcar", use_container_width=True, key="pop_btn_desmarcar_todos"):
            for c in opciones_cargos:
                st.session_state[f"chk_c_{c}"] = False
            st.rerun()

    st.markdown("<hr style='margin:8px 0; border-top:1px solid #222638;'>", unsafe_allow_html=True)

    for cargo_item in opciones_cargos:
        st.checkbox(cargo_item, key=f"chk_c_{cargo_item}")

# 2. RE-CALCULAR LISTA DE TRABAJADORES (FILTRADA POR CARGOS SELECCIONADOS EN TIEMPO REAL)
worker_options_map = {"TODO EL PERSONAL": "TODOS"}
opciones_trabajadores = ["TODO EL PERSONAL"]

if not df_trab_master_db.empty:
    df_trab_filtrado = df_trab_master_db.copy()
    if pending_cargos and 'CARGO' in df_trab_filtrado.columns:
        if pending_cargos == ["__NINGUNO__"]:
            df_trab_filtrado = df_trab_filtrado.iloc[0:0]
        else:
            cargos_set = set(pending_cargos)
            df_trab_filtrado = df_trab_filtrado[df_trab_filtrado['CARGO'].astype(str).str.strip().isin(cargos_set)]
            
    for _, r in df_trab_filtrado.iterrows():
        dni = str(r.get('DNI', '')).strip()
        ape = str(r.get('APELLIDOS', '')).strip()
        nom = str(r.get('NOMBRES', '')).strip()
        if dni and (ape or nom):
            disp = f"{dni} - {ape} {nom}".strip()
            worker_options_map[disp] = dni
            opciones_trabajadores.append(disp)

opciones_trabajadores = ["TODO EL PERSONAL"] + sorted(list(set(opciones_trabajadores[1:])))

# 3. FORMULARIO DE CONSULTA (ACTUALIZA LOS RESULTADOS SOLO AL PRESIONAR FILTRAR)
with st.sidebar.form(key="filter_form"):
    curr_idx = 0
    if st.session_state['active_worker'] in opciones_trabajadores:
        curr_idx = opciones_trabajadores.index(st.session_state['active_worker'])
    st.markdown("<p class='sidebar-field-title' style='margin-bottom:4px; font-size:0.95rem; font-weight:700; color:#ffffff;'>Filtrar por Trabajador</p>", unsafe_allow_html=True)
    trabajador_input = st.selectbox("Filtrar por Trabajador", opciones_trabajadores, index=curr_idx, label_visibility="collapsed")

    st.markdown("---")
    st.subheader("📅 Consulta por Rango de Fechas")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fecha_inicio_input = st.date_input("Fecha Inicio", value=st.session_state['active_f_ini'])
    with col_d2:
        fecha_fin_input = st.date_input("Fecha Fin", value=st.session_state['active_f_fin'])

    st.markdown("<br>", unsafe_allow_html=True)
    btn_filtrar = st.form_submit_button("🔍 FILTRAR", use_container_width=True)

if btn_filtrar:
    st.session_state['active_cargos'] = pending_cargos
    st.session_state['active_worker'] = trabajador_input
    st.session_state['active_f_ini'] = fecha_inicio_input
    st.session_state['active_f_fin'] = fecha_fin_input
    st.toast("🔍 Filtros aplicados correctamente", icon="🎯")
    st.rerun()

# 3. CARGA DE TRANSACCIONES HIKVISION
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Carga de Transacciones Hikvision")
asistencia_folder = st.sidebar.text_input("Ruta Carpeta 'Asistencia GZG'", DEFAULT_ASISTENCIA_DIR)

available_files = []
search_dir = asistencia_folder
if os.path.exists(asistencia_folder):
    available_files = [f for f in os.listdir(asistencia_folder) if f.endswith(('.xlsx', '.xlsm', '.csv'))]

if not available_files:
    # Fallback al directorio raíz del proyecto
    search_dir = "."
    available_files = [f for f in os.listdir(".") if f.startswith("Transacciones_") and f.endswith(('.xlsx', '.xlsm', '.csv'))]

available_files.sort(reverse=True)

selected_file_name = None
if available_files:
    selected_file_name = st.sidebar.selectbox("Seleccionar Archivo Descargado", available_files)

uploaded_file = st.sidebar.file_uploader("O cargar archivo manual (.xlsx, .csv)", type=["xlsm", "xlsx", "csv"])

target_file_to_load = None
if uploaded_file is not None:
    target_file_to_load = uploaded_file
elif selected_file_name:
    target_file_to_load = os.path.join(search_dir, selected_file_name)

if target_file_to_load:
    if 'last_loaded' not in st.session_state or st.session_state['last_loaded'] != str(target_file_to_load):
        st.session_state['last_loaded'] = str(target_file_to_load)
        st.toast("✅ Carga exitosa: Archivo de transacciones detectado", icon="📁")

# 4. PRUEBAS Y SIMULACIÓN
st.sidebar.markdown("---")
st.sidebar.subheader("🧪 Pruebas y Simulación")
if st.sidebar.button("⚡ Generar Lote de Pruebas (200-300 transacciones)", use_container_width=True):
    with st.spinner("Generando transacciones de prueba para agosto 2026..."):
        generated_path = generar_lote_pruebas()
        df_trab, df_marc, df_he_in = cargar_datos_excel(generated_path)
        df_trab_master, _, _ = cargar_datos_excel(BASE_EXCEL)
        if df_trab.empty:
            df_trab = df_trab_master
            
        guardar_trabajadores(df_trab)
        guardar_marcaciones_raw(df_marc, archivo_origen=generated_path)
        df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc, df_he_in, AttendanceConfig())
        guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)
        
        df_t_db, df_m_db, df_a_db, df_h_db, df_i_db = obtener_datos_db()
        guardar_excel_base(df_t_db, df_m_db, df_a_db, df_h_db, df_i_db, BASE_EXCEL)
        
        st.success(f"Lote de pruebas generado y procesado en la BD: {generated_path}")
        st.rerun()

config = AttendanceConfig()

c_act1, c_act2, c_act3 = st.columns([1.2, 1.4, 1.6])

with c_act1:
    btn_procesar = st.button("⚡ PROCESAR ASISTENCIA", use_container_width=True, type="primary")

if btn_procesar:
    if target_file_to_load is not None:
        with st.spinner("Procesando transacciones de Hikvision y guardando en BD SQLite..."):
            df_trab, df_marc, df_he_in = cargar_datos_excel(target_file_to_load)
            
            if df_trab.empty:
                df_trab, _, _, _, _ = obtener_datos_db()
                
            if not df_marc.empty and not df_trab.empty:
                guardar_marcaciones_raw(df_marc, archivo_origen=str(target_file_to_load))
                df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc, df_he_in, config)
                guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)
                
                df_t_db, df_m_db, df_a_db, df_h_db, df_i_db = obtener_datos_db()
                guardar_excel_base(df_t_db, df_m_db, df_a_db, df_h_db, df_i_db, BASE_EXCEL)
                
                st.toast("✅ Proceso exitoso: Marcaciones calculadas y guardadas en la BD y Excel base v1.0", icon="🎉")
                st.success("Proceso exitoso: Asistencia actualizada correctamente en la Base de Datos.")
            else:
                st.error("No se pudieron extraer marcaciones válidas del archivo seleccionado.")
    else:
        st.warning("Selecciona o carga un archivo de transacciones antes de procesar.")

# UTILIZAR VALORES CONFIRMADOS DEL SESSION STATE
cargos_seleccionados = st.session_state.get('active_cargos', [])
trabajador_seleccionado_disp = st.session_state['active_worker']
fecha_inicio = st.session_state['active_f_ini']
fecha_fin = st.session_state['active_f_fin']

f_ini_str = fecha_inicio.strftime("%Y-%m-%d")
f_fin_str = fecha_fin.strftime("%Y-%m-%d")

df_trab_db, df_marc_db, df_asis_db, df_he_db, df_inc_db = obtener_datos_db(f_ini_str, f_fin_str)

# APLICACIÓN MANDATORIA CON JERARQUÍA DE FILTRADO:
# PRIORIDAD 1: Si hay un Trabajador Específico seleccionado, prevalece su DNI.
# PRIORIDAD 2: Si está en 'TODOS EL PERSONAL', prevalecen los Cargos seleccionados.

if trabajador_seleccionado_disp in worker_options_map and worker_options_map[trabajador_seleccionado_disp] != "TODOS":
    selected_dni = worker_options_map[trabajador_seleccionado_disp]
    
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

elif cargos_seleccionados:
    cargos_set = set(cargos_seleccionados)
    if not df_trab_db.empty and 'CARGO' in df_trab_db.columns:
        df_trab_db = df_trab_db[df_trab_db['CARGO'].astype(str).str.strip().isin(cargos_set)]
        
    if not df_asis_db.empty and 'CARGO' in df_asis_db.columns:
        df_asis_db = df_asis_db[df_asis_db['CARGO'].astype(str).str.strip().isin(cargos_set)]
        
    if not df_inc_db.empty and 'CARGO' in df_inc_db.columns:
        df_inc_db = df_inc_db[df_inc_db['CARGO'].astype(str).str.strip().isin(cargos_set)]
        
    if not df_he_db.empty and 'CARGO' in df_he_db.columns:
        df_he_db = df_he_db[df_he_db['CARGO'].astype(str).str.strip().isin(cargos_set)]

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

with c_act2:
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

with c_act3:
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

        # FILA 1: 8 TARJETAS KPI CAJÓN
        k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
        
        with k1:
            st.markdown(f'''
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">PERSONAL TOTAL</div>
                    <div class="kpi-cajon-single-number">{tot_personal}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
        with k2:
            st.markdown(f'''
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(34, 197, 94, 0.15); color: #22c55e;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">PRESENTES</div>
                    <div class="kpi-cajon-single-number">{total_presentes}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with k3:
            st.markdown(f'''
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(148, 163, 184, 0.15); color: #94a3b8;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">AUSENTES</div>
                    <div class="kpi-cajon-single-number">{total_ausentes}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with k4:
            st.markdown(f'''
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">TARDANZAS</div>
                    <div class="kpi-cajon-single-number">{total_tardanzas}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with k5:
            st.markdown(f'''
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(168, 85, 247, 0.15); color: #a855f7;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42C17.99 7.86 19 9.81 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-2.19 1.01-4.14 2.58-5.42L6.17 5.17C4.23 6.82 3 9.26 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">EXCESO JORNADA</div>
                    <div class="kpi-cajon-single-number">{exceso_fmt}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with k6:
            st.markdown(f'''
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">HORAS EXTRA H.E.</div>
                    <div class="kpi-cajon-single-number">{he_fmt}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with k7:
            st.markdown(f'''
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(239, 68, 68, 0.15); color: #ef4444;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">INCIDENCIAS</div>
                    <div class="kpi-cajon-single-number">{total_incidencias}</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with k8:
            st.markdown(f'''
            <div class="kpi-cajon-single">
                <div class="kpi-icon-badge" style="background: rgba(236, 72, 153, 0.15); color: #ec4899;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>
                </div>
                <div class="kpi-text-block">
                    <div class="kpi-cajon-single-title">SALIDAS ANTICIPADAS</div>
                    <div class="kpi-cajon-single-number">{total_salidas_ant}</div>
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
                fig_bar = px.bar(
                    cargo_counts, x='CARGO', y='Cantidad', color='ESTADO ASISTENCIA',
                    color_discrete_map=COLOR_MAP_ESTADOS, barmode='stack', text='Cantidad', height=460
                )
                fig_bar.update_traces(textposition='outside', textfont=dict(color='#ffffff', size=13, weight='bold'))
                fig_bar.update_layout(
                    paper_bgcolor='#090a0f', plot_bgcolor='#090a0f',
                    font=dict(color='#ffffff', size=13, family='Segoe UI, sans-serif'),
                    xaxis=dict(title=dict(text='Cargo', font=dict(color='#ffffff', size=14)), tickfont=dict(color='#ffffff', size=12), showgrid=False),
                    yaxis=dict(title=dict(text='Cantidad de Registros', font=dict(color='#ffffff', size=14)), tickfont=dict(color='#ffffff', size=12), showgrid=True, gridcolor='#1c1e29'),
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

        # FILA 4: RANKINGS TOP 10 EJECUTIVOS
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏆 Rankings Ejecutivos - Top 10 Incidencias, Tardanzas y Horas Extra</div>', unsafe_allow_html=True)

        col_top1, col_top2, col_top3 = st.columns(3)

        with col_top1:
            st.markdown('''
            <div class="top10-container">
                <div class="top10-title-yellow">⚠️ TOP 10 TARDANZAS</div>
            ''', unsafe_allow_html=True)
            if 'TARDANZA (MIN)' in df_asis_db.columns:
                df_tard_rank = df_asis_db.copy()
                df_tard_rank['MINUTOS'] = to_numeric_minutes(df_tard_rank['TARDANZA (MIN)'])
                df_tard_sum = df_tard_rank.groupby(['DNI', 'APELLIDOS', 'NOMBRES'])['MINUTOS'].sum().reset_index()
                df_tard_sum = df_tard_sum[df_tard_sum['MINUTOS'] > 0].sort_values(by='MINUTOS', ascending=False).head(10)
                
                if not df_tard_sum.empty:
                    rows_html = ""
                    for idx, (_, r) in enumerate(df_tard_sum.iterrows(), start=1):
                        nombre = f"{r['APELLIDOS']} {r['NOMBRES']}".strip()
                        if len(nombre) > 22:
                            nombre = nombre[:20] + ".."
                        min_str = format_hhmm(r['MINUTOS'])
                        rows_html += f"<tr><td class='top10-num'>#{idx}</td><td style='text-align:left;'>{nombre}</td><td>{min_str}</td></tr>"
                    
                    st.markdown(f'''
                    <table class="top10-table-custom">
                        <thead><tr><th>#</th><th style="text-align:left;">Personal</th><th>HH:MM</th></tr></thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("Sin tardanzas registradas.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_top2:
            st.markdown('''
            <div class="top10-container">
                <div class="top10-title-blue">⏱️ TOP 10 HORAS EXTRA</div>
            ''', unsafe_allow_html=True)
            if not df_he_db.empty:
                col_he_target = 'DURACIÓN' if 'DURACIÓN' in df_he_db.columns else 'DURACIÓN (HH:MM)'
                df_he_rank = df_he_db.copy()
                df_he_rank['MINUTOS'] = to_numeric_minutes(df_he_rank[col_he_target])
                df_he_sum = df_he_rank.groupby(['DNI', 'APELLIDOS', 'NOMBRES'])['MINUTOS'].sum().reset_index()
                df_he_sum = df_he_sum[df_he_sum['MINUTOS'] > 0].sort_values(by='MINUTOS', ascending=False).head(10)
                
                if not df_he_sum.empty:
                    rows_html = ""
                    for idx, (_, r) in enumerate(df_he_sum.iterrows(), start=1):
                        nombre = f"{r['APELLIDOS']} {r['NOMBRES']}".strip()
                        if len(nombre) > 22:
                            nombre = nombre[:20] + ".."
                        min_str = format_hhmm(r['MINUTOS'])
                        rows_html += f"<tr><td class='top10-num' style='color:#3b82f6;'>#{idx}</td><td style='text-align:left;'>{nombre}</td><td>{min_str}</td></tr>"
                    
                    st.markdown(f'''
                    <table class="top10-table-custom">
                        <thead><tr><th>#</th><th style="text-align:left;">Personal</th><th>HH:MM</th></tr></thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("Sin horas extra registradas.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_top3:
            st.markdown('''
            <div class="top10-container">
                <div class="top10-title-red">🚨 TOP 10 INCIDENCIAS</div>
            ''', unsafe_allow_html=True)
            if not df_inc_db.empty:
                df_inc_rank = df_inc_db.groupby(['DNI', 'APELLIDOS', 'NOMBRES']).size().reset_index(name='CANTIDAD')
                df_inc_rank = df_inc_rank.sort_values(by='CANTIDAD', ascending=False).head(10)
                
                if not df_inc_rank.empty:
                    rows_html = ""
                    for idx, (_, r) in enumerate(df_inc_rank.iterrows(), start=1):
                        nombre = f"{r['APELLIDOS']} {r['NOMBRES']}".strip()
                        if len(nombre) > 20:
                            nombre = nombre[:18] + ".."
                        rows_html += f"<tr><td class='top10-num' style='color:#ef4444;'>#{idx}</td><td style='text-align:left;'>{nombre}</td><td>{r['CANTIDAD']} reg.</td></tr>"
                    
                    st.markdown(f'''
                    <table class="top10-table-custom">
                        <thead><tr><th>#</th><th style="text-align:left;">Personal</th><th>Total</th></tr></thead>
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
