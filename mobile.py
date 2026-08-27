import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import time
import os
import sys
import base64

def signal_ready():
    """No-op: El iframe padre de la PWA detecta la carga de forma nativa e instantánea sin inyectar iframes en el DOM."""
    pass

# Asegurar importaciones del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.database import (
    init_db, obtener_solicitudes_aprobacion, actualizar_estado_aprobacion,
    sincronizar_aprobaciones_desde_asistencia, sincronizar_aprobaciones_con_gdrive,
    regenerar_aprobaciones_excel, guardar_sustento_trabajador,
    cambiar_password_usuario, obtener_usuario_by_username,
    crear_token_sesion, validar_token_sesion, eliminar_token_sesion
)
from core.auth import init_auth, is_authenticated, login_user, logout_user, get_current_user, hash_password, verify_password

from PIL import Image

import json

@st.cache_data(show_spinner=False)
def get_file_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data(show_spinner=False)
def get_logo_base64():
    """Obtiene el logo oficial transparente de GZG en Base64."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for logo_name in ["gzg_logo_transparent.png", "gzg_logo.png", "gzg_logo_clean.png"]:
        logo_path = os.path.join(root_dir, "assets", logo_name)
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data(show_spinner=False)
def get_hero_base64():
    """Obtiene la imagen de portada minera para el login."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for hero_name in ["login_mining_hero.jpg", "login_hero.jpg"]:
        hero_path = os.path.join(root_dir, "assets", hero_name)
        if os.path.exists(hero_path):
            with open(hero_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data(show_spinner=False)
def get_worker_avatar_url(dni: str, worker_name: str) -> str:
    if dni:
        dni_clean = str(dni).strip().lstrip('0').zfill(8)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        for ext in ['.jpg', '.jpeg', '.png']:
            for folder in [os.path.join(root_dir, 'assets', 'fotos'), os.path.join(root_dir, 'assets', 'fotos_trabajadores')]:
                p = os.path.join(folder, f"{dni_clean}{ext}")
                if os.path.exists(p):
                    try:
                        with open(p, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                            mime = "image/png" if ext == '.png' else "image/jpeg"
                            return f"data:{mime};base64,{b64}"
                    except Exception:
                        pass
    # Generación 100% local en SVG (0ms latencia, sin peticiones de red externas)
    partes = str(worker_name).strip().split()
    initials = ("".join([p[0] for p in partes if p])[:2]).upper() if partes else "GZ"
    svg_data = f'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80"><circle cx="40" cy="40" r="40" fill="#F58220"/><text x="50%" y="54%" font-family="sans-serif" font-size="28" font-weight="bold" fill="#FFFFFF" text-anchor="middle" dominant-baseline="middle">{initials}</text></svg>'
    b64_svg = base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64_svg}"

def parse_adjuntos(val) -> list:
    """Extrae una lista de URLs/Base64/Rutas de adjuntos desde la base de datos."""
    if not val or pd.isna(val):
        return []
    v_str = str(val).strip()
    if v_str.lower() in ('none', 'nan', ''):
        return []
    if "|||" in v_str:
        return [x.strip() for x in v_str.split("|||") if x.strip()]
    elif v_str.startswith("[") and v_str.endswith("]"):
        try:
            import json
            res = json.loads(v_str)
            if isinstance(res, list): return res
        except Exception:
            pass
    return [v_str]

logo_b64 = get_logo_base64()
hero_b64 = get_hero_base64()
icon192_b64 = get_file_b64("assets/icon-192.png") or logo_b64
icon512_b64 = get_file_b64("assets/icon-512.png") or logo_b64

manifest_dict = {
    "name": "GZG MINERALES",
    "short_name": "GZG MINERALES",
    "description": "Sistema de Control de Asistencia y Aprobaciones Móviles - GZG Minerales",
    "start_url": "./",
    "scope": "/",
    "display": "standalone",
    "orientation": "portrait-primary",
    "background_color": "#121418",
    "theme_color": "#121418",
    "lang": "es",
    "icons": [
        {
            "src": f"data:image/png;base64,{icon192_b64}",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": f"data:image/png;base64,{icon512_b64}",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable"
        }
    ]
}
manifest_b64 = base64.b64encode(json.dumps(manifest_dict).encode()).decode()

logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 45px; margin-right: 10px; vertical-align: middle;">' if logo_b64 else ''
logo_icon = Image.open("assets/icon-192.png") if os.path.exists("assets/icon-192.png") else (Image.open("assets/gzg_logo.png") if os.path.exists("assets/gzg_logo.png") else "📱")

# Configuración de página 100% enfocada en Celular (Centrado sin Sidebar)
st.set_page_config(
    page_title="GZG MINERALES",
    page_icon=logo_icon,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Fondo sólido base - SIEMPRE presente, sin importar el estado de login.
# Esto elimina el parpadeo porque nunca se agrega ni se quita del DOM.
st.markdown("""
<div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -2; background: #121418; pointer-events: none;"></div>
""", unsafe_allow_html=True)

# Inicializar Base de Datos y Autenticación
if "db_initialized" not in st.session_state:
    init_db()
    init_auth()
    st.session_state["db_initialized"] = True

# ---------------------------------------------------------
# AUTO-LOGIN PERSISTENTE SI "RECORDARME" ESTÁ ACTIVO
# ---------------------------------------------------------
if not is_authenticated():
    if not st.session_state.get('just_logged_out', False):
        persisted_token = st.query_params.get("token", "")
        if persisted_token:
            user_data = validar_token_sesion(persisted_token)
            if user_data and user_data.get("activo", 1) == 1:
                st.session_state["authenticated"] = True
                st.session_state["user"] = {
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "nombre_completo": user_data["nombre_completo"],
                    "rol": user_data["rol"],
                    "area_asignada": user_data["area_asignada"],
                    "cargo": user_data.get("cargo", "")
                }
    else:
        st.session_state['just_logged_out'] = False

# Inyectar metas para icono y PWA
st.markdown(f"""
<head>
    <title>GZG MINERALES</title>
    <meta name="apple-mobile-web-app-title" content="GZG MINERALES">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#121418">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <link rel="manifest" href="data:application/manifest+json;base64,{manifest_b64}">
    <link rel="apple-touch-icon" href="app/static/icon-192.png">
    <link rel="apple-touch-icon" href="data:image/png;base64,{icon192_b64}">
    <link rel="icon" type="image/png" sizes="192x192" href="app/static/icon-192.png">
    <link rel="icon" type="image/png" sizes="192x192" href="data:image/png;base64,{icon192_b64}">
    <link rel="icon" type="image/png" sizes="512x512" href="app/static/icon-512.png">
    <link rel="icon" type="image/png" sizes="512x512" href="data:image/png;base64,{icon512_b64}">
    <link rel="shortcut icon" href="app/static/favicon.png">
</head>
""", unsafe_allow_html=True)

# CSS TOTALMENTE AISLADO PARA CELULARES (Hides all desktop elements & prevents flickering)
st.markdown("""
<style>
    /* =====================================================================
       FONDO OSCURO NATIVO PWA GZG (100% ESTÁTICO SIN PARPADEO)
       ===================================================================== */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background-color: transparent !important;
        background: transparent !important;
        color: #FFFFFF !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
    }

    /* Desactivar oscurecimiento y parpadeo al recargar en Streamlit */
    *, *::before, *::after {
        transition: none !important;
        animation: none !important;
    }
    .stApp,
    .stApp[data-test-script-state="running"],
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"][data-test-script-state="running"],
    div[data-testid="stVerticalBlock"],
    div[data-testid="stVerticalBlock"][data-test-script-state="running"],
    div.block-container,
    div.block-container[data-test-script-state="running"] {
        opacity: 1 !important;
        filter: none !important;
    }

    /* Padding compacto superior e inferior para vista móvil */
    .main .block-container {
        padding: 0.2rem 0.5rem 50px 0.5rem !important;
        max-width: 500px !important;
        margin: 0 auto !important;
        width: 100% !important;
    }

    /* =====================================================================
       CAPA 1: OCULTAR SKELETONS Y PLACEHOLDERS (sin ocultar contenido real)
       ===================================================================== */
    [data-testid="stSkeleton"],
    .stSkeleton,
    div[class*="skeleton"],
    div[class*="Skeleton"],
    [data-testid="stStatusWidget"],
    div[data-testid="stDecoration"],
    div[class*="StatusWidget"],
    div[class*="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        width: 0px !important;
    }

    /* =====================================================================
       CAPA 4: OCULTAR BARRA SUPERIOR Y ELEMENTOS DE STREAMLIT CLOUD
       ===================================================================== */
    header,
    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    #MainMenu,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    .stDeployButton,
    div[class*="viewerBadge"],
    div[class*="StatusWidget"],
    div[class*="Toolbar"],
    div[class*="Header"],
    div[class*="accessibility"],
    button[aria-label="Manage app"],
    div[data-testid="stDecoration"],
    section[data-testid="stSidebar"],
    div[data-testid="stSidebarCollapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        height: 0px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* =====================================================================
       CAPA 5: OCULTAR FOOTER Y BADGE DE STREAMLIT CLOUD
       ===================================================================== */
    footer,
    footer[data-testid="stFooter"],
    [data-testid="stFooter"],
    div[class*="viewerBadge"],
    div[class*="styles_viewerBadge"],
    div[class*="viewerBadge_container"],
    div[class*="FloatingProfile"],
    div[data-testid="stEmbedCode"],
    div[data-testid="stBottom"],
    div[data-testid="stBottomBlockContainer"],
    div[class*="stAppDeployButton"],
    div:has(> a[href*="streamlit.io"]),
    div:has(> a[href*="github.com"]),
    a[href*="streamlit.io"],
    a[href*="github.com"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        width: 0px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }



    /* Formulario de Login: Contenedor con efecto Glassmorphism */
    div[data-testid="stForm"] {
        background: rgba(22, 25, 32, 0.92) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 18px !important;
        padding: 20px 18px !important;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.75) !important;
    }

    /* Respuesta táctil inmediata al 1er toque en celulares */
    button,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"],
    .stButton > button {
        touch-action: manipulation !important;
        -webkit-tap-highlight-color: transparent !important;
        cursor: pointer !important;
    }

    /* Bordes e inputs */
    div[data-baseweb="input"],
    .stTextInput > div > div,
    div[data-testid="stFileUploader"] {
        border: 1px solid #2A2F3D !important;
        border-radius: 10px !important;
        background-color: #1A1D24 !important;
    }
    div[data-baseweb="input"]:focus-within, .stTextInput > div > div:focus-within {
        border: 1px solid #F58220 !important;
        box-shadow: 0 0 0 1px rgba(245, 130, 32, 0.3) !important;
    }

    /* Estilo limpio para inputs de texto en Login y Formularios */
    .stTextInput input,
    input[type="text"],
    input[type="password"] {
        color: #FFFFFF !important;
        font-size: 15px !important;
        text-align: left !important;
        background-color: #1A1D24 !important;
        border-radius: 10px !important;
        caret-color: #F58220 !important;
        padding-left: 12px !important;
    }

    /* Autofill limpio en navegadores móviles */
    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus,
    input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 50px #1A1D24 inset !important;
        -webkit-text-fill-color: #FFFFFF !important;
        caret-color: #F58220 !important;
    }

    /* Texto blanco en todos los inputs del form */
    .stTextInput input, input[type="text"], input[type="password"] {
        color: #FFFFFF !important;
        font-size: 15px !important;
        text-align: left !important;
    }
    .stTextInput label p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    /* Ocultar instrucción "Press Enter to submit form" */
    [data-testid="InputInstructions"], .stInputInstructions {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        opacity: 0 !important;
    }

    /* Cabecera Móvil GZG */
    .mobile-header {
        background: linear-gradient(185deg, #1D212A 0%, #121418 100%);
        padding: 16px;
        border-bottom: 1px solid #2A2F3D;
        margin-bottom: 16px;
        border-radius: 14px;
        width: 100%;
    }
    .gzg-logo-text {
        font-family: 'Arial Black', sans-serif;
        font-size: 22px;
        letter-spacing: 2px;
        color: #FFFFFF;
    }
    .gzg-orange {
        color: #F58220 !important;
    }

    /* Tarjetas de Aprobación Móvil */
    .approval-card {
        background-color: #1A1D24;
        border: 1px solid #2A2F3D;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .worker-name {
        font-size: 16px;
        font-weight: 700;
        color: #FFFFFF;
    }
    .worker-role {
        font-size: 12px;
        color: #9A9EA7;
    }

    /* Badges de Estado — 100% Indestructibles y Sin Partir en Móvil */
    .badge-approved {
        background-color: rgba(39, 174, 96, 0.2) !important;
        color: #27AE60 !important;
        border: 1px solid #27AE60 !important;
        padding: 3px 9px !important;
        border-radius: 12px !important;
        font-size: 10.5px !important;
        font-weight: 800 !important;
        letter-spacing: 0.3px !important;
        white-space: nowrap !important;
        display: inline-block !important;
        flex-shrink: 0 !important;
    }
    .badge-rejected {
        background-color: rgba(231, 76, 60, 0.2) !important;
        color: #E74C3C !important;
        border: 1px solid #E74C3C !important;
        padding: 3px 9px !important;
        border-radius: 12px !important;
        font-size: 10.5px !important;
        font-weight: 800 !important;
        letter-spacing: 0.3px !important;
        white-space: nowrap !important;
        display: inline-block !important;
        flex-shrink: 0 !important;
    }
    .badge-pending {
        background-color: rgba(243, 156, 18, 0.2) !important;
        color: #F39C12 !important;
        border: 1px solid #F39C12 !important;
        padding: 3px 9px !important;
        border-radius: 12px !important;
        font-size: 10.5px !important;
        font-weight: 800 !important;
        letter-spacing: 0.3px !important;
        white-space: nowrap !important;
        display: inline-block !important;
        flex-shrink: 0 !important;
    }

    /* Botones táctiles */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 44px !important;
        touch-action: manipulation !important;
    }

    /* FORZAR FILA HORIZONTAL ÚNICA EN TODAS LAS PANTALLAS (MÓVIL, TABLET, PC) */
    [data-testid="stHorizontalBlock"],
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
        max-width: 100% !important;
        gap: 8px !important;
        box-sizing: border-box !important;
        margin: 0 0 10px 0 !important;
        padding: 0 !important;
    }

    @media (max-width: 768px), (max-width: 640px) {
        [data-testid="stHorizontalBlock"],
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            gap: 8px !important;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="column"],
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"] > div {
            flex: 1 1 calc(50% - 4px) !important;
            width: calc(50% - 4px) !important;
            max-width: calc(50% - 4px) !important;
            min-width: 0px !important;
            box-sizing: border-box !important;
        }

        [data-testid="stHorizontalBlock"] .stButton,
        [data-testid="stHorizontalBlock"] button {
            width: 100% !important;
            min-width: 0px !important;
            height: 38px !important;
            font-size: 13px !important;
            padding: 0 4px !important;
        }
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 50% !important;
        width: 50% !important;
        max-width: calc(50% - 4px) !important;
        min-width: 0px !important;
        display: flex !important;
        align-items: center !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stHorizontalBlock"] .stButton,
    div[data-testid="stHorizontalBlock"] button {
        width: 100% !important;
        min-width: 0px !important;
        height: 38px !important;
        min-height: 38px !important;
        padding: 0 6px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        border-radius: 9px !important;
        margin: 0 !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Botón Rechazar — Rojo Carmesí Sólido Sin Borde (Solo st.button dentro de Expander) */
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-secondary"],
    div[data-testid="stExpander"] div.stButton button[kind="secondary"] {
        background: linear-gradient(135deg, #C0392B 0%, #962D22 100%) !important;
        background-color: #C0392B !important;
        background-image: linear-gradient(135deg, #C0392B 0%, #962D22 100%) !important;
        border: none !important;
        outline: none !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 12px rgba(192, 57, 43, 0.35) !important;
        margin-bottom: 0px !important;
    }
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-secondary"] p,
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-secondary"] span,
    div[data-testid="stExpander"] div.stButton button[kind="secondary"] p,
    div[data-testid="stExpander"] div.stButton button[kind="secondary"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stExpander"] div.stButton button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #D9383A 0%, #B02A2B 100%) !important;
        background-color: #D9383A !important;
        color: #FFFFFF !important;
    }

    /* Botón Aprobar — Naranja Corporativo Sin Borde y Pegado Sutilmente a Rechazar */
    div[data-testid="stExpander"] div.stButton button[kind="primary"],
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #F58220 0%, #D35400 100%) !important;
        background-color: #F58220 !important;
        background-image: linear-gradient(135deg, #F58220 0%, #D35400 100%) !important;
        border: none !important;
        outline: none !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 14px rgba(245, 130, 32, 0.35) !important;
        margin-top: -3px !important;
    }
    div[data-testid="stExpander"] div.stButton button[kind="primary"] p,
    div[data-testid="stExpander"] div.stButton button[kind="primary"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Botones de Aprobación en Modo Apagado / Gris cuando están deshabilitados */
    div[data-testid="stExpander"] div.stButton button:disabled,
    div[data-testid="stExpander"] div.stButton button[disabled],
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-secondary"]:disabled,
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-primary"]:disabled,
    div[data-testid="stExpander"] div.stButton button[kind="secondary"]:disabled,
    div[data-testid="stExpander"] div.stButton button[kind="primary"]:disabled,
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-secondary"][disabled],
    div[data-testid="stExpander"] div.stButton button[data-testid="baseButton-primary"][disabled],
    div[data-testid="stExpander"] div.stButton button[kind="secondary"][disabled],
    div[data-testid="stExpander"] div.stButton button[kind="primary"][disabled] {
        background: #232730 !important;
        background-color: #232730 !important;
        background-image: none !important;
        border: 1px solid #333846 !important;
        color: #6B7280 !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
        opacity: 0.45 !important;
        pointer-events: none !important;
    }
    div[data-testid="stExpander"] div.stButton button:disabled p,
    div[data-testid="stExpander"] div.stButton button:disabled span,
    div[data-testid="stExpander"] div.stButton button[disabled] p,
    div[data-testid="stExpander"] div.stButton button[disabled] span,
    div[data-testid="stExpander"] div.stButton button[kind="secondary"]:disabled p,
    div[data-testid="stExpander"] div.stButton button[kind="secondary"]:disabled span,
    div[data-testid="stExpander"] div.stButton button[kind="primary"]:disabled p,
    div[data-testid="stExpander"] div.stButton button[kind="primary"]:disabled span {
        color: #6B7280 !important;
        font-weight: 600 !important;
    }

    /* Cabecera uniforme en 2 líneas limpias para tarjetas de solicitud expandibles */
    div[data-testid="stExpander"] details summary,
    div[data-testid="stExpander"] summary {
        padding: 8px 12px !important;
    }
    div[data-testid="stExpander"] details summary p,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] {
        white-space: pre-line !important;
        line-height: 1.45 !important;
    }

    /* File Uploader: Botón Upload en Tono Gris Neutro Original (Garantizado) */
    div[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploader"] [data-testid="baseButton-secondary"],
    section[data-testid="stFileUploadDropzone"] button,
    div[data-testid="stExpander"] div[data-testid="stFileUploader"] button,
    div[data-testid="stExpander"] section[data-testid="stFileUploadDropzone"] button {
        background: #1D212A !important;
        background-color: #1D212A !important;
        background-image: none !important;
        border: 1px solid #2A2F3D !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
        margin-bottom: 0 !important;
    }
    div[data-testid="stFileUploader"] button p,
    div[data-testid="stFileUploader"] button span,
    div[data-testid="stExpander"] div[data-testid="stFileUploader"] button p,
    div[data-testid="stExpander"] div[data-testid="stFileUploader"] button span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    div[data-testid="stFileUploader"] button:hover,
    div[data-testid="stExpander"] div[data-testid="stFileUploader"] button:hover {
        background: #262B37 !important;
        background-color: #262B37 !important;
        border-color: #3B4254 !important;
    }

    /* PUNTO 7: Popover Clave — Respuesta Inmediata al Primer Toque */
    [data-testid="stPopover"] > button {
        touch-action: manipulation !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    div[data-testid="stPopoverBody"] {
        z-index: 999999 !important;
        border: 1px solid #2A2F3D !important;
        background: #1A1D24 !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8) !important;
    }

    /* Estilo de pestañas superiores en celular */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        gap: 4px !important;
        margin-top: 0px !important;
        margin-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------
# PANTALLA DE LOGIN MÓVIL CON FONDO MINERO GZG CORPORATIVO
# ---------------------------------------------------------
if not is_authenticated():
    # Foto minera HD que se apila sobre el fondo sólido (-1 sobre -2)
    if hero_b64:
        st.markdown(f"""
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; background: linear-gradient(180deg, rgba(14, 16, 20, 0.0) 0%, rgba(14, 16, 20, 0.20) 38%, #0E1014 85%), url('data:image/jpeg;base64,{hero_b64}') no-repeat center top; background-size: cover; background-attachment: fixed;"></div>
        """, unsafe_allow_html=True)

    # 1. Cabecera Superior Corporativa (Logo y Títulos arriba bien pegados al tope)
    st.markdown(f"""
<div style="text-align: center; padding: 0px 0 0px 0; margin-top: -3.8rem;">
    <div style="margin-bottom: 2px;">
        <img src="data:image/png;base64,{logo_b64}" style="height: 58px; object-fit: contain; filter: drop-shadow(0 6px 16px rgba(0,0,0,0.8));">
    </div>
    <div style="font-size: 24px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; line-height: 1.1; margin-bottom: 2px; text-shadow: 0 2px 10px rgba(0,0,0,0.9);">
        <span style="color: #FFFFFF;">GZG</span> <span style="color: #F58220;">MINERALES</span>
    </div>
    <div style="font-size: 10px; font-weight: 700; color: #E0E2EC; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 0px; opacity: 0.95; text-shadow: 0 2px 8px rgba(0,0,0,0.9);">
        APLICACION MOVIL PARA APROBACIONES
    </div>
</div>
""", unsafe_allow_html=True)

    # 2. Espacio visual para despejar la maquinaria minera del centro
    st.markdown("<div style='height: 14vh; min-height: 90px;'></div>", unsafe_allow_html=True)

    # 3. Bloque de Bienvenida bajado hacia el formulario
    st.markdown("""
<div style="text-align: left; margin-bottom: 8px;">
    <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px; text-shadow: 0 2px 8px rgba(0,0,0,0.9);">Bienvenido</div>
    <div style="font-size: 12px; color: #C5CAD3; text-shadow: 0 1px 6px rgba(0,0,0,0.9);">Inicia sesión para continuar</div>
</div>
""", unsafe_allow_html=True)
    
    # Formulario atómico para empaquetar credenciales de forma robusta en celular
    with st.form("form_login_mobile", clear_on_submit=False):
        u_name = st.text_input("Usuario", placeholder="")
        u_pass = st.text_input("Contraseña", type="password", placeholder="")
        
        col_rec, _ = st.columns([1.5, 1])
        with col_rec:
            recordarme = st.toggle("Recordarme", value=True, key="chk_recordarme_login")
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        btn_login = st.form_submit_button("🔑 INGRESAR", type="primary", use_container_width=True)
        if btn_login:
            if u_name and u_pass:
                if login_user(u_name.strip(), u_pass.strip()):
                    st.session_state['just_logged_out'] = False
                    if recordarme:
                        new_token = crear_token_sesion(u_name.strip())
                        st.query_params["token"] = new_token
                    else:
                        if "token" in st.query_params:
                            del st.query_params["token"]
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
            else:
                st.warning("Por favor ingresa tu usuario y contraseña.")

    st.markdown("""
<div style="width: 100%; text-align: center; margin-top: 28px; margin-bottom: 20px; font-size: 13px; font-weight: 600; color: #8A8E97; letter-spacing: 0.8px;">
    Creado por raules v1.0.0
</div>
""", unsafe_allow_html=True)
    
    signal_ready()
    st.stop()

# ---------------------------------------------------------
# APLICACIÓN MÓVIL PWA PRINCIPAL (USUARIOS AUTENTICADOS)
# ---------------------------------------------------------
current_user = get_current_user()
if current_user:
    # Recargar datos frescos de la BD para reflejar cambios inmediatos de rol/cargo
    db_user_fresh = obtener_usuario_by_username(current_user.get('username', ''))
    if db_user_fresh:
        current_user = db_user_fresh
        st.session_state['user'] = db_user_fresh

username = current_user.get('username', 'Supervisor') if current_user else 'Supervisor'
rol = current_user.get('rol', 'SUPERVISOR') if current_user else 'SUPERVISOR'

# Formatear nombre corto para el saludo (Primer Nombre y Apellido Paterno)
def get_user_display_name(u_dict, u_name):
    if not u_dict:
        return u_name.title()
    u = u_dict.get('username', u_name).lower().strip()
    MAPA_SALUDOS = {
        'admin': 'Administración',
        'jagreda': 'Jhon Ágreda',
        'jalva': 'Jhon Alva',
        'jdelariva': 'Javier De La Riva',
        'jhuayama': 'Josmell Huayama',
        'msanchez': 'Manuel Sánchez',
        'lpretel': 'Liliana Pretel',
        'respinoza': 'Raúl Espinoza',
        'jsanchez': 'Juan Sánchez',
    }
    if u in MAPA_SALUDOS:
        return MAPA_SALUDOS[u]
    
    dni = str(u_dict.get('dni', '') or '').strip().lstrip('0').zfill(8)
    if dni and dni != '00000000':
        try:
            conn = get_connection()
            r = conn.execute("SELECT nombres, apellidos FROM trabajadores WHERE dni = ?", (dni,)).fetchone()
            conn.close()
            if r:
                p_nom = str(r[0] or '').strip().split()[0] if r[0] else ''
                p_ape = str(r[1] or '').strip().split()[0] if r[1] else ''
                if p_nom and p_ape:
                    return f"{p_nom} {p_ape}".title()
        except Exception:
            pass

    nombre_comp = u_dict.get('nombre_completo', '')
    if nombre_comp:
        partes = nombre_comp.strip().split()
        if len(partes) >= 2:
            return f"{partes[0]} {partes[1]}".title()
        return nombre_comp.title()
    return u_name.title()

def format_worker_name(nombres_str, apellidos_str):
    """Retorna obligatoriamente el primer nombre y los apellidos completos (ej. Yenkli Ordoñez Arteaga)."""
    noms = str(nombres_str or '').strip().split()
    primer_nom = noms[0] if noms else ''
    apells = str(apellidos_str or '').strip()
    if primer_nom and apells:
        return f"{primer_nom} {apells}".title()
    elif primer_nom:
        return primer_nom.title()
    return apells.title()

def clean_hhmm(val):
    """Normaliza cualquier formato '01:45', '1h 45m', 105 a 'HH:MM' consistente."""
    if val is None or pd.isna(val):
        return '00:00'
    s = str(val).strip()
    if not s or s.lower() in ('none', 'nan', '-'):
        return '00:00'
    if ':' in s:
        parts = s.split(':')
        try:
            h = int(parts[0])
            m = int(parts[1])
            return f"{h:02d}:{m:02d}"
        except Exception:
            return s
    import re
    m_match = re.search(r'(\d+)\s*h\s*(\d+)?\s*m?', s, re.IGNORECASE)
    if m_match:
        h = int(m_match.group(1))
        m = int(m_match.group(2)) if m_match.group(2) else 0
        return f"{h:02d}:{m:02d}"
    try:
        total_m = int(float(s))
        return f"{total_m // 60:02d}:{total_m % 60:02d}"
    except Exception:
        return s

nombre_saludo = get_user_display_name(current_user, username)

# Cabecera Central Corporativa GZG en Dashboard
st.markdown(f"""
<div style="text-align: center; padding: 0 0 2px 0; margin-top: -2.8rem;">
    <div style="margin-bottom: 2px;">
        <img src="data:image/png;base64,{logo_b64}" style="height: 44px; object-fit: contain; filter: drop-shadow(0 4px 14px rgba(0,0,0,0.55));">
    </div>
    <div style="font-size: 18px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; line-height: 1.1; margin-bottom: 2px;">
        <span style="color: #FFFFFF;">GZG</span> <span style="color: #F58220;">MINERALES</span>
    </div>
    <div style="font-size: 10px; font-weight: 700; color: #E0E2EC; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px; opacity: 0.95;">
        CONTROL DE HORAS EXTRAS
    </div>
</div>

<div style="background: rgba(26, 29, 36, 0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 8px 12px; margin-top: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
    <div style="font-size: 13.5px; font-weight: 800; color: #FFFFFF;">
        Hola, {nombre_saludo} 👋
    </div>
    <div style="font-size: 10.5px; font-weight: 700; color: #F58220; background: rgba(245, 130, 32, 0.15); border: 1px solid rgba(245, 130, 32, 0.3); border-radius: 6px; padding: 2px 8px; letter-spacing: 0.5px; text-transform: uppercase;">
        {rol}
    </div>
</div>
""", unsafe_allow_html=True)

signal_ready()

# Callbacks atómicos para ejecución inmediata en el primer toque táctil
def callback_logout():
    # 1. PRIMERO: Limpiar el estado de sesión en memoria inmediatamente
    logout_user()
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    st.session_state['just_logged_out'] = True
    st.session_state['show_change_pw_box'] = False

    # 2. SEGUNDO: Limpiar base de datos SQLite protegida contra bloqueos
    try:
        _cur_token = st.query_params.get('token', '')
        eliminar_token_sesion(token=_cur_token, username=username)
    except Exception:
        pass

    # 3. TERCERO: Limpiar query_params de URL al final
    try:
        if "token" in st.query_params:
            del st.query_params["token"]
        st.query_params.clear()
    except Exception:
        pass

def callback_toggle_pw():
    st.session_state["show_change_pw_box"] = not st.session_state.get("show_change_pw_box", False)
    if st.session_state.get("show_change_pw_box", False):
        st.session_state["pw_change_success"] = False

# Mensaje de confirmación de cambio de contraseña exitoso (En el tope visual)
if st.session_state.get("pw_change_success", False):
    st.success("✅ **¡Contraseña actualizada exitosamente!** Tu nueva clave ya está guardada y activa.")
    st.toast("🎉 ¡Contraseña actualizada exitosamente!", icon="🔑")
    if st.button("✖ Entendido / Cerrar aviso", key="btn_close_pw_success", use_container_width=True):
        st.session_state["pw_change_success"] = False
        st.rerun()

# 2 Botones Nativos Gemelos Simétricos (50% Cambiar clave a la izquierda / 50% Salir a la derecha)
col_b1, col_b2 = st.columns(2)
with col_b1:
    st.button("🔑 Cambiar clave", key="btn_toggle_change_pw", on_click=callback_toggle_pw, use_container_width=True)

with col_b2:
    st.button("🚪 Salir", key="btn_logout_mobile", on_click=callback_logout, use_container_width=True)

# Formulario desplegable para cambiar contraseña al pulsar el botón Clave
if st.session_state.get("show_change_pw_box", False):
    with st.container():
        st.markdown("""
        <div style="background: rgba(245, 130, 32, 0.08); border: 1px solid rgba(245, 130, 32, 0.25); border-radius: 10px; padding: 12px 14px; margin-bottom: 12px;">
            <div style="font-size: 14px; font-weight: 700; color: #F58220; margin-bottom: 4px;">🔑 Cambiar mi Contraseña</div>
            <div style="font-size: 11px; color: #D1D5DB;">💡 Ingresa tu contraseña actual y escribe la nueva clave (mínimo 6 caracteres).</div>
        </div>
        """, unsafe_allow_html=True)
        
        p_act_h = st.text_input("Contraseña Actual", type="password", key="inp_pw_act")
        p_nue_h = st.text_input("Nueva Contraseña", type="password", placeholder="Mínimo 6 caracteres", key="inp_pw_nue")
        p_cnf_h = st.text_input("Confirmar Nueva Contraseña", type="password", placeholder="Repite la nueva contraseña", key="inp_pw_cnf")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            btn_h_pw = st.button("💾 Guardar", type="primary", key="btn_save_new_pw", use_container_width=True)
        with col_f2:
            btn_h_close = st.button("✖ Cancelar", key="btn_cancel_new_pw", use_container_width=True)
        
        if btn_h_close:
            st.session_state["show_change_pw_box"] = False
            st.rerun()
            
        if btn_h_pw:
            u_curr = username.strip().lower()
            db_u = obtener_usuario_by_username(u_curr)
            if not p_act_h:
                st.error("❌ Por favor ingresa tu contraseña actual.")
                st.toast("❌ Falta contraseña actual", icon="⚠️")
            elif not db_u or not verify_password(p_act_h.strip(), db_u.get('password_hash', ''), u_curr):
                st.error("❌ La contraseña actual ingresada es incorrecta.")
                st.toast("❌ Contraseña actual incorrecta", icon="⚠️")
            elif not p_nue_h or len(p_nue_h.strip()) < 6:
                st.warning("⚠️ La nueva contraseña debe tener al menos 6 caracteres.")
                st.toast("⚠️ Mínimo 6 caracteres requeridos", icon="⚠️")
            elif p_nue_h.strip() != p_cnf_h.strip():
                st.error("❌ Las nuevas contraseñas no coinciden.")
                st.toast("❌ Las contraseñas no coinciden", icon="⚠️")
            else:
                new_h = hash_password(p_nue_h.strip())
                if cambiar_password_usuario(u_curr, new_h):
                    try:
                        eliminar_token_sesion(username=u_curr)
                    except Exception:
                        pass
                    if st.session_state.get("user"):
                        st.session_state["user"]["password_hash"] = new_h
                    st.session_state["show_change_pw_box"] = False
                    st.session_state["pw_change_success"] = True
                    try:
                        st.session_state["inp_pw_act"] = ""
                        st.session_state["inp_pw_nue"] = ""
                        st.session_state["inp_pw_cnf"] = ""
                    except Exception:
                        pass
                    st.toast("🎉 ¡Contraseña actualizada exitosamente!", icon="🔑")
                    st.rerun()
                else:
                    st.error("❌ Error interno al actualizar la contraseña en la base de datos.")




# ---------------------------------------------------------
# SISTEMA DE NOTIFICACIONES WEB PUSH PWA
# ---------------------------------------------------------
try:
    from core.push_notifications import obtener_o_crear_claves_vapid, guardar_suscripcion_push
    vapid_k = obtener_o_crear_claves_vapid()
    vapid_pub = vapid_k.get("public_key_b64", "")
    
    if "push_sub" in st.query_params:
        try:
            import urllib.parse
            sub_raw = urllib.parse.unquote(st.query_params["push_sub"])
            sub_data = json.loads(sub_raw)
            guardar_suscripcion_push(username, sub_data)
            del st.query_params["push_sub"]
            st.toast("🔔 ¡Notificaciones push activadas en este dispositivo!", icon="📱")
        except Exception:
            pass

    # Verificar si el usuario ya tiene suscripciones push activas en la BD
    from core.push_notifications import inicializar_tabla_push
    inicializar_tabla_push()
    conn_p = get_connection(DB_PATH)
    cur_p = conn_p.cursor()
    cur_p.execute("SELECT COUNT(*) FROM push_subscriptions WHERE username = ?", (username.strip().lower(),))
    has_push = (cur_p.fetchone()[0] > 0)
    conn_p.close()

    btn_text = "✅ Alertas Activas en este Celular" if has_push else "🔔 Activar Alertas de Aprobación en Celular"
    btn_color = "#2ECC71" if has_push else "#F58220"
    btn_border = "rgba(46, 204, 113, 0.4)" if has_push else "rgba(245, 130, 32, 0.4)"
    btn_bg = "rgba(46, 204, 113, 0.1)" if has_push else "linear-gradient(135deg, rgba(245, 130, 32, 0.15) 0%, rgba(245, 130, 32, 0.05) 100%)"

    # Inyección de script JS para registro de Service Worker y suscripción a Web Push
    st.components.v1.html(f"""
    <div id="push_card_container" style="margin-bottom: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
      <button id="btn_push_req" onclick="solicitarPermisoPush()" style="
        width: 100%;
        background: {btn_bg};
        border: 1px solid {btn_border};
        border-radius: 10px;
        padding: 10px 14px;
        color: {btn_color};
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        box-sizing: border-box;
      ">
        {btn_text}
      </button>
    </div>

    <script>
    function urlBase64ToUint8Array(base64String) {{
      const padding = '='.repeat((4 - base64String.length % 4) % 4);
      const base64 = (base64String + padding).replace(/\\-/g, '+').replace(/_/g, '/');
      const rawData = window.atob(base64);
      const outputArray = new Uint8Array(rawData.length);
      for (let i = 0; i < rawData.length; ++i) {{
        outputArray[i] = rawData.charCodeAt(i);
      }}
      return outputArray;
    }}

    // Escuchar respuesta de la ventana principal (si corre dentro del wrapper PWA de GitHub Pages)
    window.addEventListener('message', function(event) {{
      if (event.data && event.data.type === 'GZG_PUSH_SUB_SUCCESS' && event.data.sub) {{
        const subStr = encodeURIComponent(event.data.sub);
        try {{
          const curUrl = new URL(window.top.location.href);
          curUrl.searchParams.set('push_sub', subStr);
          window.top.location.replace(curUrl.toString());
        }} catch(e) {{
          const curUrl = new URL(window.location.href);
          curUrl.searchParams.set('push_sub', subStr);
          window.location.replace(curUrl.toString());
        }}
      }}
    }});

    async function solicitarPermisoPush() {{
      const btn = document.getElementById('btn_push_req');
      
      // 1. Si estamos dentro de un iframe (GitHub Pages PWA Wrapper), solicitar permiso a la ventana principal (window.top)
      if (window.top && window.top !== window) {{
        window.top.postMessage({{ type: 'GZG_REQUEST_PUSH', vapid_pub: "{vapid_pub}" }}, '*');
        return;
      }}

      // 2. Si estamos directo en la web de Streamlit
      if (!('Notification' in window)) {{
        alert('Este navegador no soporta notificaciones push.');
        return;
      }}

      try {{
        const perm = await Notification.requestPermission();
        if (perm === 'granted') {{
          const reg = await navigator.serviceWorker.register('/sw.js');
          await navigator.serviceWorker.ready;
          let sub = await reg.pushManager.getSubscription();
          if (!sub) {{
            sub = await reg.pushManager.subscribe({{
              userVisibleOnly: true,
              applicationServerKey: urlBase64ToUint8Array("{vapid_pub}")
            }});
          }}
          const subStr = encodeURIComponent(JSON.stringify(sub));
          const curUrl = new URL(window.location.href);
          curUrl.searchParams.set('push_sub', subStr);
          window.location.replace(curUrl.toString());
        }} else if (perm === 'denied') {{
          alert('Las notificaciones están bloqueadas en tu navegador. Ve a Configuración de Sitios y selecciona Permitir.');
        }}
      }} catch(err) {{
        console.error('Error al suscribir push:', err);
      }}
    }}
    </script>
    """, height=50)
except Exception:
    pass


# Cargar data de aprobaciones directamente de SQLite sin bloqueos de red
df_all_raw = obtener_solicitudes_aprobacion('TODAS')

# PUNTO 7: Filtrado por bandeja personal del usuario autenticado
if rol not in ('ADMINISTRADOR', 'ADMINISTRACION', 'ADMIN') and 'aprobador_n1' in df_all_raw.columns:
    mask = (
        df_all_raw['aprobador_n1'].fillna('').str.lower().str.strip() == username.lower().strip()
    ) | (
        df_all_raw['aprobador_n2'].fillna('').str.lower().str.strip() == username.lower().strip()
    )
    df_all = df_all_raw[mask].copy()
else:
    df_all = df_all_raw.copy()


# Mapeo de DNI del usuario autenticado para la gestión de sus horas personales
MAPA_USUARIOS_DNI = {
    'admin': '',
    'jagreda': '47783594',
    'jalva': '47034929',
    'jdelariva': '72559194',
    'jhuayama': '46671923',
    'msanchez': '26696602',
    'lpretel': '75227437',
    'respinoza': '44955960',
    'jsanchez': '70782038',
}
user_dni = str(current_user.get('dni', '') or '').strip().lstrip('0').zfill(8) if current_user else ''
if (not user_dni or user_dni == '00000000') and username.lower().strip() in MAPA_USUARIOS_DNI:
    user_dni = MAPA_USUARIOS_DNI[username.lower().strip()]

# Determinar si el usuario es aprobador con personal a cargo o personal operativo/general
u_lower = username.lower().strip()
aprobadores_n1 = set(df_all_raw['aprobador_n1'].dropna().str.lower().str.strip().unique()) if 'aprobador_n1' in df_all_raw.columns else set()
aprobadores_n2 = set(df_all_raw['aprobador_n2'].dropna().str.lower().str.strip().unique()) if 'aprobador_n2' in df_all_raw.columns else set()
todos_aprobadores = (aprobadores_n1.union(aprobadores_n2)) - {'', '-', 'none', 'nan'}

es_aprobador = (rol in ('ADMINISTRADOR', 'ADMINISTRACION', 'ADMIN', 'SUPERVISOR', 'JEFE', 'GERENCIA', 'SUPERINTENDENTE')) or (u_lower in todos_aprobadores)

# Pestañas Móviles PWA dinámicas según el rol
if not es_aprobador:
    # Usuarios que NO son aprobadores: MIS HORAS EXTRAS PRIMERO, luego Historial y Dashboard (Sin pestaña Pendientes)
    tab_mis_horas, tab_historial, tab_dashboard = st.tabs([
        "📝 Mis Horas Extras", "📜 Historial", "📊 Dashboard"
    ])
    tab_pendientes = None
else:
    # Aprobadores y Jefes con personal a cargo: PENDIENTES PRIMERO, luego Historial, Dashboard y Mis Horas Extras
    tab_pendientes, tab_historial, tab_dashboard, tab_mis_horas = st.tabs([
        "📋 Pendientes", "📜 Historial", "📊 Dashboard", "📝 Mis Horas Extras"
    ])

# ---------------------------------------------------------
# CÁLCULO UNIFICADO Y CORRELACIONADO DE BANDEJAS POR ROL
# ---------------------------------------------------------
df_raw_dni = df_all_raw['dni'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lstrip('0').str.zfill(8)
df_mis_horas = df_all_raw[df_raw_dni == user_dni].copy() if user_dni and user_dni != '00000000' else pd.DataFrame()

if rol in ('ADMINISTRADOR', 'ADMINISTRACION', 'ADMIN'):
    df_pendientes = df_all[df_all['estado'] == 'PENDIENTE'].copy()
    df_aprobadas_mes = df_all[df_all['estado'] == 'APROBADO'].copy()
    df_rechazadas_mes = df_all[df_all['estado'] == 'RECHAZADO'].copy()
elif es_aprobador:
    # 1. PENDIENTES: Lo que REQUIERE acción inmediata del usuario
    # Regla Jerárquica Estricta: Nivel 2 solo visualiza y puede aprobar cuando Nivel 1 ya aprobó
    tiene_n1 = df_all['aprobador_n1'].fillna('').str.strip().ne('') & ~df_all['aprobador_n1'].fillna('').str.lower().isin(['-', 'none', 'nan'])
    n1_aprobado_o_inexistente = (df_all['estado_n1'] == 'APROBADO') | (~tiene_n1)

    is_pend_for_me = (
        (df_all['aprobador_n1'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n1'] == 'PENDIENTE')
    ) | (
        (df_all['aprobador_n2'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n2'] == 'PENDIENTE') & (df_all['estado_n1'] != 'RECHAZADO') & n1_aprobado_o_inexistente
    )
    df_pendientes = df_all[is_pend_for_me & (df_all['estado'] != 'RECHAZADO')].copy()
    
    # 2. APROBADAS: Solicitudes donde el usuario ya dio su aprobación o terminaron aprobadas
    is_app_by_me = (
        (df_all['aprobador_n1'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n1'] == 'APROBADO')
    ) | (
        (df_all['aprobador_n2'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n2'] == 'APROBADO')
    ) | (df_all['estado'] == 'APROBADO')
    df_aprobadas_mes = df_all[is_app_by_me].copy()

    # 3. RECHAZADAS: Solicitudes rechazadas por el usuario o en la cadena
    is_rej_by_me = (
        (df_all['aprobador_n1'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n1'] == 'RECHAZADO')
    ) | (
        (df_all['aprobador_n2'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n2'] == 'RECHAZADO')
    ) | (df_all['estado'] == 'RECHAZADO')
    df_rechazadas_mes = df_all[is_rej_by_me].copy()
else:
    df_pendientes = df_mis_horas[df_mis_horas['estado'] == 'PENDIENTE'].copy()
    df_aprobadas_mes = df_mis_horas[df_mis_horas['estado'] == 'APROBADO'].copy()
    df_rechazadas_mes = df_mis_horas[df_mis_horas['estado'] == 'RECHAZADO'].copy()

# ---------------------------------------------------------
# ---------------------------------------------------------
# TAB 1: PENDIENTES DE APROBACIÓN (EVALUACIÓN POR NIVEL)
# ---------------------------------------------------------
def render_tab_pendientes():
    # Cajones de Métricas en una Sola Fila 50% / 50% para Celular
    st.markdown(f"""
    <div style="display: flex; flex-direction: row; gap: 8px; width: 100%; margin-bottom: 15px; box-sizing: border-box;">
        <!-- Izquierda 50%: Pendientes (Naranja) -->
        <div style="flex: 1 1 50%; width: 50%; background: linear-gradient(135deg, #F58220 0%, #D35400 100%); border-radius: 10px; padding: 7px 6px; text-align: center; box-shadow: 0 3px 10px rgba(245, 130, 32, 0.25); box-sizing: border-box;">
            <div style="font-size: 20px; font-weight: 900; color: #FFFFFF; line-height: 1.1;">{len(df_pendientes)}</div>
            <div style="font-size: 11px; font-weight: 700; color: #FFFFFF; letter-spacing: 0.3px;">Pendientes</div>
        </div>
        <!-- Derecha 50%: Aprobadas este mes (Celeste) -->
        <div style="flex: 1 1 50%; width: 50%; background: linear-gradient(135deg, #0288D1 0%, #0277BD 100%); border-radius: 10px; padding: 7px 6px; text-align: center; box-shadow: 0 3px 10px rgba(2, 136, 209, 0.3); box-sizing: border-box;">
            <div style="font-size: 20px; font-weight: 900; color: #FFFFFF; line-height: 1.1;">{len(df_aprobadas_mes)}</div>
            <div style="font-size: 11px; font-weight: 700; color: #FFFFFF; letter-spacing: 0.3px;">Aprobadas este mes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if df_pendientes.empty:
        st.info("🎉 ¡Excelente! No tienes solicitudes pendientes en este momento.")
    else:
        for idx, row in df_pendientes.iterrows():
            sol_id = row['id']
            worker_name = format_worker_name(row.get('nombres', ''), row.get('apellidos', ''))
            cargo = row.get('cargo', 'Operativo')
            fecha_sol = row.get('fecha', '')
            he_hhmm = clean_hhmm(row.get('horas_extras_hhmm', '00:00'))
            exceso_hhmm = clean_hhmm(row.get('exceso_jornada_hhmm', '00:00'))
            jornada_hhmm = clean_hhmm(row.get('jornada_trabajada_hhmm', '-'))
            inicio_he = str(row.get('inicio_he') or '').strip()
            fin_he = str(row.get('fin_he') or '').strip()
            if inicio_he.lower() in ('none', 'nan'): inicio_he = ""
            if fin_he.lower() in ('none', 'nan'): fin_he = ""
            he_detail = f" <span style='color: #9A9EA7; font-size: 11.5px; font-weight: 500;'>({inicio_he} a {fin_he})</span>" if inicio_he and fin_he and he_hhmm != '00:00' else ""

            avatar_url = get_worker_avatar_url(row.get('dni'), worker_name)
            
            # Verificar sustento y definir estado para la cabecera contraída
            obs_trab = str(row.get('observacion_trabajador', '') or '').strip()
            if obs_trab.lower() in ('none', 'nan'): obs_trab = ""
            adj_list = parse_adjuntos(row.get('adjuntos'))
            tiene_sustento = bool(obs_trab or adj_list)

            with st.expander(f"👤 **{worker_name}** ({fecha_sol})\n⏰ {he_hhmm}  |  ⚠️ {exceso_hhmm}", expanded=False):
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; margin: 6px 0 10px 0;">
                    <img src="{avatar_url}" style="width: 42px; height: 42px; border-radius: 50%; border: 2px solid #F58220; object-fit: cover; flex-shrink: 0;" />
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">{worker_name}</div>
                        <div style="font-size: 12px; color: #9A9EA7;">{cargo} ({fecha_sol})</div>
                    </div>
                </div>

                <div style="margin: 6px 0 10px 0; font-size: 13px; line-height: 1.6; color: #D1D5DB;">
                    <div>🕒 <strong style="color: #FFFFFF;">Entrada:</strong> <code style="background: rgba(255,255,255,0.08); padding: 1px 6px; border-radius: 4px; color: #2ECC71;">{row.get('entrada', '-')}</code> &nbsp;|&nbsp; <strong style="color: #FFFFFF;">Salida:</strong> <code style="background: rgba(255,255,255,0.08); padding: 1px 6px; border-radius: 4px; color: #2ECC71;">{row.get('salida', '-')}</code></div>
                    <div>⏱️ <strong style="color: #FFFFFF;">Jornada trabajada:</strong> {jornada_hhmm}</div>
                    <div>⏰ <strong style="color: #FFFFFF;">Horas extras:</strong> <b style="color: #F58220;">{he_hhmm}</b>{he_detail}</div>
                    <div>⚠️ <strong style="color: #FFFFFF;">Exceso de jornada:</strong> <b style="color: #E67E22;">{exceso_hhmm}</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar sustento personal del trabajador si existe
                if obs_trab:
                    st.markdown(f"""
                    <div style="background: rgba(52, 152, 219, 0.12); border-left: 3px solid #3498DB; padding: 7px 10px; border-radius: 6px; margin: 8px 0; font-size: 12px; color: #FFFFFF;">
                        <strong style="color: #3498DB;">👤 Sustento de {worker_name}:</strong><br>
                        <span style="color: #E5E7EB;">{obs_trab}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Mostrar validación previa de Nivel 1 si ya fue aprobada por el supervisor
                c_n1_prev = str(row.get('comentario_n1', '') or '').strip()
                if c_n1_prev and c_n1_prev.lower() not in ('none', 'nan', ''):
                    ap_n1_name = str(row.get('aprobado_por_n1', '') or 'Supervisor').strip()
                    st.markdown(f"""
                    <div style="background: rgba(46, 204, 113, 0.12); border-left: 3px solid #2ECC71; padding: 7px 10px; border-radius: 6px; margin: 8px 0; font-size: 12px; color: #FFFFFF;">
                        <strong style="color: #2ECC71;">✅ Validación Nivel 1 ({ap_n1_name}):</strong><br>
                        <span style="color: #E5E7EB;">{c_n1_prev}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Mostrar fotos previas si existen
                adj_list = parse_adjuntos(row.get('adjuntos'))
                if adj_list:
                    ap_n1_name = str(row.get('aprobado_por_n1', '') or 'Nivel 1').strip()
                    if len(adj_list) == 1:
                        st.image(adj_list[0], caption=f"📷 Foto adjuntada por {ap_n1_name}", use_container_width=True)
                    else:
                        st.markdown(f"<div style='font-size: 12px; font-weight: 700; color: #F58220; margin: 6px 0 4px 0;'>📷 Fotos adjuntas ({len(adj_list)} fotos):</div>", unsafe_allow_html=True)
                        for i in range(0, len(adj_list), 2):
                            c_img1, c_img2 = st.columns(2)
                            with c_img1:
                                st.image(adj_list[i], caption=f"Foto {i+1}", use_container_width=True)
                            if i + 1 < len(adj_list):
                                with c_img2:
                                    st.image(adj_list[i+1], caption=f"Foto {i+2}", use_container_width=True)

                # Regla de Bloqueo Inteligente para N2 (Reporte Directo a Gerencia)
                app_n1_raw = str(row.get('aprobador_n1') or '').strip().lower()
                app_n2_raw = str(row.get('aprobador_n2') or '').strip().upper()
                is_direct_to_gerencia = (app_n1_raw == 'msanchez') and (app_n2_raw in ('NA', '-', '', 'NAN', 'NONE'))
                tiene_sustento = bool(obs_trab or adj_list)
                is_blocked_for_n2 = is_direct_to_gerencia and (not tiene_sustento)

                if is_blocked_for_n2:
                    st.markdown("""
                    <div style="background: rgba(241, 196, 15, 0.12); border-left: 3px solid #F1C40F; padding: 7px 10px; border-radius: 6px; margin: 8px 0; font-size: 12px; color: #F1C40F;">
                        ⏳ <strong>Esperando Sustento:</strong> El trabajador/jefe aún no ha enviado su justificación ni fotos desde su app móvil. Los botones de aprobación se activarán cuando envíe su sustento.
                    </div>
                    """, unsafe_allow_html=True)

                comentario_aprobador = st.text_input(
                    "✍️ Comentario del Aprobador",
                    key=f"m_com_{sol_id}",
                    placeholder=""
                )
                
                uploaded_files = st.file_uploader(
                    "📷 Adjuntar Fotos (permite múltiples)",
                    type=["png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key=f"m_file_{sol_id}"
                )
                
                # 2 Botones Gemelos Simétricos 50% / 50% en Fila Horizontal
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("❌ RECHAZAR", key=f"m_rej_{sol_id}", disabled=is_blocked_for_n2, use_container_width=True):
                        adjunto_rel_path = None
                        if uploaded_files:
                            root_dir = os.path.dirname(os.path.abspath(__file__))
                            adj_dir = os.path.join(root_dir, "downloads", "adjuntos_aprobaciones")
                            os.makedirs(adj_dir, exist_ok=True)
                            data_uris = []
                            for f_idx, uf in enumerate(uploaded_files):
                                fname = f"solic_{sol_id}_{f_idx}_{uf.name}"
                                fpath = os.path.join(adj_dir, fname)
                                buf = uf.getvalue()
                                with open(fpath, "wb") as f:
                                    f.write(buf)
                                mime = "image/png" if uf.name.lower().endswith('.png') else "image/jpeg"
                                b64_img = base64.b64encode(buf).decode()
                                data_uris.append(f"data:{mime};base64,{b64_img}")
                            if data_uris:
                                adjunto_rel_path = "|||".join(data_uris)

                        actualizar_estado_aprobacion(sol_id, 'RECHAZADO', username, comentario_aprobador, adjunto_rel_path)
                        st.toast(f"❌ Rechazado: {worker_name}", icon="ℹ️")
                        st.rerun()

                with col_act2:
                    if st.button("✅ APROBAR", key=f"m_app_{sol_id}", type="primary", disabled=is_blocked_for_n2, use_container_width=True):
                        adjunto_rel_path = None
                        if uploaded_files:
                            root_dir = os.path.dirname(os.path.abspath(__file__))
                            adj_dir = os.path.join(root_dir, "downloads", "adjuntos_aprobaciones")
                            os.makedirs(adj_dir, exist_ok=True)
                            data_uris = []
                            for f_idx, uf in enumerate(uploaded_files):
                                fname = f"solic_{sol_id}_{f_idx}_{uf.name}"
                                fpath = os.path.join(adj_dir, fname)
                                buf = uf.getvalue()
                                with open(fpath, "wb") as f:
                                    f.write(buf)
                                mime = "image/png" if uf.name.lower().endswith('.png') else "image/jpeg"
                                b64_img = base64.b64encode(buf).decode()
                                data_uris.append(f"data:{mime};base64,{b64_img}")
                            if data_uris:
                                adjunto_rel_path = "|||".join(data_uris)

                        actualizar_estado_aprobacion(sol_id, 'APROBADO', username, comentario_aprobador, adjunto_rel_path)
                        st.toast(f"✅ Aprobado: {worker_name}", icon="🎉")
                        st.rerun()

if tab_pendientes is not None:
    with tab_pendientes:
        render_tab_pendientes()

# ---------------------------------------------------------
# TAB 2: HISTORIAL DE APROBACIONES (CORRELACIONADO CON USUARIO)
# ---------------------------------------------------------
with tab_historial:
    filtro_estado = st.radio("Estado:", ["TODAS", "APROBADAS", "RECHAZADAS"], horizontal=True, key="rad_m_hist")
    
    if filtro_estado == "APROBADAS":
        df_hist = df_aprobadas_mes.copy()
    elif filtro_estado == "RECHAZADAS":
        df_hist = df_rechazadas_mes.copy()
    else:
        df_hist = df_all.copy() if es_aprobador else df_mis_horas.copy()
        
    if df_hist.empty:
        st.info("No hay registros en el historial para este filtro.")
    else:
        cards_list = []
        for idx, row in df_hist.iterrows():
            worker_name = format_worker_name(row.get('nombres', ''), row.get('apellidos', ''))
            cargo = row.get('cargo', '')
            fecha_sol = row.get('fecha', '')
            estado_global = str(row.get('estado', 'PENDIENTE')).upper()
            estado_n1 = str(row.get('estado_n1', 'PENDIENTE')).upper()
            estado_n2 = str(row.get('estado_n2', 'PENDIENTE')).upper()
            he_hhmm = clean_hhmm(row.get('horas_extras_hhmm', '00:00'))
            exceso_hhmm = clean_hhmm(row.get('exceso_jornada_hhmm', '00:00'))
            inicio_he = str(row.get('inicio_he') or '').strip()
            fin_he = str(row.get('fin_he') or '').strip()
            if inicio_he.lower() in ('none', 'nan'): inicio_he = ""
            if fin_he.lower() in ('none', 'nan'): fin_he = ""
            he_detail = f" <span style='color: #9A9EA7; font-size: 11px;'>({inicio_he} a {fin_he})</span>" if inicio_he and fin_he and he_hhmm != '00:00' else ""
            
            # Badge descriptivo inteligente según estado de nivel
            if estado_global == 'APROBADO':
                badge_html = '<span class="badge-approved">APROBADO FINAL</span>'
            elif estado_global == 'RECHAZADO' or estado_n1 == 'RECHAZADO' or estado_n2 == 'RECHAZADO':
                badge_html = '<span class="badge-rejected">RECHAZADO</span>'
            elif estado_n1 == 'APROBADO':
                badge_html = '<span class="badge-approved" style="background-color: rgba(46, 204, 113, 0.15); border-color: #2ECC71;">APROBADO N1</span>'
            else:
                badge_html = '<span class="badge-pending">PENDIENTE</span>'
            
            # Detalle de quién aprobó / validó
            aprob_info = []
            if row.get('aprobado_por_n1'):
                aprob_info.append(f"N1: {row.get('aprobado_por_n1')} ({estado_n1})")
            if row.get('aprobado_por_n2'):
                aprob_info.append(f"N2: {row.get('aprobado_por_n2')} ({estado_n2})")
            aprob_str = " | ".join(aprob_info) if aprob_info else f"Por: {row.get('aprobado_por') or 'Pendiente'}"
            
            # Comentarios de N1 y N2 en historial
            c_info_str = ""
            c1 = str(row.get('comentario_n1', '') or '').strip()
            c2 = str(row.get('comentario_n2', '') or '').strip()
            csup = str(row.get('comentario_supervisor', '') or '').strip()
            cmts = []
            if c1 and c1.lower() not in ('none', 'nan'): cmts.append(f"<b>N1:</b> {c1}")
            if c2 and c2.lower() not in ('none', 'nan'): cmts.append(f"<b>N2:</b> {c2}")
            if not cmts and csup and csup.lower() not in ('none', 'nan'): cmts.append(f"<b>Obs:</b> {csup}")
            if cmts:
                c_info_str = f"""<div style="font-size: 11px; color: #D1D5DB; background: rgba(255,255,255,0.04); padding: 5px 8px; border-radius: 4px; margin-top: 6px; line-height: 1.4;">{'<br>'.join(cmts)}</div>"""
            
            # Foto adjunta si existe
            adj_html = ""
            adj_list_hist = parse_adjuntos(row.get('adjuntos'))
            if adj_list_hist:
                imgs_tags = "".join([f'<img src="{x}" style="max-width: 48%; max-height: 140px; border-radius: 6px; object-fit: cover; border: 1px solid #3A3F4D; margin: 2px;" />' for x in adj_list_hist])
                adj_html = f"""<div style="margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px;">{imgs_tags}</div>"""

            cards_list.append(f"""<div class="approval-card">
<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; width: 100%;">
<div class="worker-name" style="flex: 1 1 auto; min-width: 0; word-break: break-word; line-height: 1.25;">{worker_name}</div>
<div style="flex-shrink: 0; white-space: nowrap; padding-top: 1px;">{badge_html}</div>
</div>
<div class="worker-role">{cargo} ({fecha_sol})</div>
<hr style="border-color: #2A2F3D; margin: 8px 0;">
<div style="font-size: 12px; line-height: 1.5;">
<div>⏰ H.E.: <b style="color: #F58220;">{he_hhmm}</b>{he_detail}</div>
<div>⚠️ Exceso: <b style="color: #E67E22;">{exceso_hhmm}</b></div>
</div>
{c_info_str}
{adj_html}
<div style="font-size: 10px; color: #9A9EA7; margin-top: 6px;">{aprob_str}</div>
</div>""")
        st.markdown("\n".join(cards_list), unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: DASHBOARD DE ESTADÍSTICAS (100% CORRELACIONADO)
# ---------------------------------------------------------
with tab_dashboard:
    n_aprob = len(df_aprobadas_mes)
    n_rech = len(df_rechazadas_mes)
    n_pend = len(df_pendientes)
    
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.metric("Aprobadas", f"{n_aprob}")
    with col_d2:
        st.metric("Rechazadas", f"{n_rech}")
    with col_d3:
        st.metric("Pendientes", f"{n_pend}")
    
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    if (n_aprob + n_rech + n_pend) > 0:
        chart_df = pd.DataFrame({
            'Estado': ['Aprobadas', 'Rechazadas', 'Pendientes'],
            'Cantidad': [n_aprob, n_rech, n_pend]
        })
        st.bar_chart(chart_df.set_index('Estado'))

# ---------------------------------------------------------
# TAB 4: MIS HORAS EXTRAS (JUSTIFICACIÓN Y SUSTENTO PERSONAL)
# ---------------------------------------------------------
with tab_mis_horas:
    if not user_dni or user_dni == '00000000':
        st.info("ℹ️ Como Administrador, visualiza y gestiona las horas de todo el personal desde la pestaña Pendientes e Historial.")
    else:
        df_raw_dni = df_all_raw['dni'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lstrip('0').str.zfill(8)
        df_mis_horas = df_all_raw[df_raw_dni == user_dni].copy()
        
        # Cajones de Métricas Personales
        n_mis_sol = len(df_mis_horas)
        mis_he_min = df_mis_horas['horas_extras_min'].sum() if 'horas_extras_min' in df_mis_horas.columns and not df_mis_horas.empty else 0
        mis_exc_min = df_mis_horas['exceso_jornada_min'].sum() if 'exceso_jornada_min' in df_mis_horas.columns and not df_mis_horas.empty else 0
        
        he_tot_hhmm = f"{int(mis_he_min // 60):02d}:{int(mis_he_min % 60):02d}"
        exc_tot_hhmm = f"{int(mis_exc_min // 60):02d}:{int(mis_exc_min % 60):02d}"
        
        st.markdown(f"""
        <div style="display: flex; flex-direction: row; gap: 8px; width: 100%; margin-bottom: 15px; box-sizing: border-box;">
            <div style="flex: 1 1 50%; width: 50%; background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); border-radius: 10px; padding: 7px 6px; text-align: center; box-shadow: 0 3px 10px rgba(30, 136, 229, 0.25); box-sizing: border-box;">
                <div style="font-size: 18px; font-weight: 900; color: #FFFFFF; line-height: 1.1;">{he_tot_hhmm}</div>
                <div style="font-size: 11px; font-weight: 700; color: #FFFFFF; letter-spacing: 0.3px;">Mis H.E. este mes</div>
            </div>
            <div style="flex: 1 1 50%; width: 50%; background: linear-gradient(135deg, #FB8C00 0%, #EF6C00 100%); border-radius: 10px; padding: 7px 6px; text-align: center; box-shadow: 0 3px 10px rgba(251, 140, 0, 0.3); box-sizing: border-box;">
                <div style="font-size: 18px; font-weight: 900; color: #FFFFFF; line-height: 1.1;">{exc_tot_hhmm}</div>
                <div style="font-size: 11px; font-weight: 700; color: #FFFFFF; letter-spacing: 0.3px;">Mis Excesos este mes</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if df_mis_horas.empty:
            st.info("🎉 ¡Excelente! No tienes horas extras ni excesos de jornada pendientes en este mes.")
        else:
            for idx, row in df_mis_horas.iterrows():
                sol_id = row['id']
                fecha_sol = row.get('fecha', '')
                he_hhmm = clean_hhmm(row.get('horas_extras_hhmm', '00:00'))
                exceso_hhmm = clean_hhmm(row.get('exceso_jornada_hhmm', '00:00'))
                jornada_hhmm = clean_hhmm(row.get('jornada_trabajada_hhmm', '-'))
                inicio_he = str(row.get('inicio_he') or '').strip()
                fin_he = str(row.get('fin_he') or '').strip()
                if inicio_he.lower() in ('none', 'nan'): inicio_he = ""
                if fin_he.lower() in ('none', 'nan'): fin_he = ""
                he_detail = f" <span style='color: #9A9EA7; font-size: 11.5px; font-weight: 500;'>({inicio_he} a {fin_he})</span>" if inicio_he and fin_he and he_hhmm != '00:00' else ""

                estado_global = str(row.get('estado', 'PENDIENTE')).upper()
                estado_n1 = str(row.get('estado_n1', 'PENDIENTE')).upper()
                estado_n2 = str(row.get('estado_n2', 'PENDIENTE')).upper()
                obs_actual = str(row.get('observacion_trabajador', '') or '').strip()
                if obs_actual.lower() in ('none', 'nan'): obs_actual = ""
                adj_list_my = parse_adjuntos(row.get('adjuntos'))
                tiene_sustento_my = bool(obs_actual or adj_list_my)

                if estado_global == 'APROBADO':
                    tag_estado_my = "✅ Aprobado"
                elif estado_global == 'RECHAZADO':
                    tag_estado_my = "❌ Rechazado"
                elif tiene_sustento_my:
                    tag_estado_my = "📩 Enviado"
                else:
                    tag_estado_my = "⏳ Pendiente"

                worker_name_me = format_worker_name(row.get('nombres', ''), row.get('apellidos', ''))
                cargo_me = row.get('cargo', 'Operativo')
                avatar_url_me = get_worker_avatar_url(row.get('dni'), worker_name_me)

                with st.expander(f"👤 **{worker_name_me}** ({fecha_sol})\n⏰ {he_hhmm}  |  ⚠️ {exceso_hhmm}  |  {tag_estado_my}", expanded=False):
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 12px; margin: 6px 0 10px 0;">
                        <img src="{avatar_url_me}" style="width: 42px; height: 42px; border-radius: 50%; border: 2px solid #F58220; object-fit: cover; flex-shrink: 0;" />
                        <div>
                            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">{worker_name_me}</div>
                            <div style="font-size: 12px; color: #9A9EA7;">{cargo_me} ({fecha_sol})</div>
                        </div>
                    </div>

                    <div style="margin: 6px 0 10px 0; font-size: 13px; line-height: 1.6; color: #D1D5DB;">
                        <div>🕒 <strong style="color: #FFFFFF;">Entrada:</strong> <code style="background: rgba(255,255,255,0.08); padding: 1px 6px; border-radius: 4px; color: #2ECC71;">{row.get('entrada', '-')}</code> &nbsp;|&nbsp; <strong style="color: #FFFFFF;">Salida:</strong> <code style="background: rgba(255,255,255,0.08); padding: 1px 6px; border-radius: 4px; color: #2ECC71;">{row.get('salida', '-')}</code></div>
                        <div>⏱️ <strong style="color: #FFFFFF;">Jornada trabajada:</strong> {jornada_hhmm}</div>
                        <div>⏰ <strong style="color: #FFFFFF;">Horas extras:</strong> <b style="color: #F58220;">{he_hhmm}</b>{he_detail}</div>
                        <div>⚠️ <strong style="color: #FFFFFF;">Exceso de jornada:</strong> <b style="color: #E67E22;">{exceso_hhmm}</b></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar sustento ya registrado si existe
                    if obs_actual:
                        st.markdown(f"""
                        <div style="background: rgba(46, 204, 113, 0.1); border-left: 3px solid #2ECC71; padding: 7px 10px; border-radius: 6px; margin: 8px 0; font-size: 12px; color: #FFFFFF;">
                            <strong style="color: #2ECC71;">✍️ Tu Sustento Enviado:</strong><br>
                            <span style="color: #E5E7EB;">{obs_actual}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Mostrar fotos ya adjuntadas si existen
                    adj_list_my = parse_adjuntos(row.get('adjuntos'))
                    if adj_list_my:
                        st.markdown(f"<div style='font-size: 12px; font-weight: 700; color: #F58220; margin: 6px 0 4px 0;'>📷 Fotos Adjuntadas ({len(adj_list_my)} fotos):</div>", unsafe_allow_html=True)
                        for i in range(0, len(adj_list_my), 2):
                            c_my1, c_my2 = st.columns(2)
                            with c_my1:
                                st.image(adj_list_my[i], caption=f"Foto {i+1}", use_container_width=True)
                            if i + 1 < len(adj_list_my):
                                with c_my2:
                                    st.image(adj_list_my[i+1], caption=f"Foto {i+2}", use_container_width=True)

                    # Formulario para sustentar / actualizar sustento
                    st.markdown("<hr style='border-color: #2A2F3D; margin: 10px 0;'>", unsafe_allow_html=True)
                    my_obs_input = st.text_area(
                        "✍️ Motivo / Detalle del trabajo realizado",
                        value=obs_actual,
                        placeholder="",
                        key=f"my_txt_{sol_id}"
                    )
                    
                    my_uploaded_files = st.file_uploader(
                        "📷 Adjuntar Fotos (permite múltiples)",
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=True,
                        key=f"my_files_{sol_id}"
                    )
                    
                    if st.button("📤 ENVIAR", key=f"btn_send_my_{sol_id}", type="primary", use_container_width=True):
                        if not my_obs_input.strip() and not my_uploaded_files and not adj_list_my:
                            st.warning("⚠️ Por favor ingresa el motivo o adjunta al menos una foto antes de enviar.")
                        else:
                            my_adj_path = None
                            if my_uploaded_files:
                                root_dir = os.path.dirname(os.path.abspath(__file__))
                                adj_dir = os.path.join(root_dir, "downloads", "adjuntos_aprobaciones")
                                os.makedirs(adj_dir, exist_ok=True)
                                data_uris = []
                                for f_idx, uf in enumerate(my_uploaded_files):
                                    fname = f"sustento_{sol_id}_{f_idx}_{uf.name}"
                                    fpath = os.path.join(adj_dir, fname)
                                    buf = uf.getvalue()
                                    with open(fpath, "wb") as f:
                                        f.write(buf)
                                    mime = "image/png" if uf.name.lower().endswith('.png') else "image/jpeg"
                                    b64_img = base64.b64encode(buf).decode()
                                    data_uris.append(f"data:{mime};base64,{b64_img}")
                                if data_uris:
                                    my_adj_path = "|||".join(data_uris)

                            if guardar_sustento_trabajador(sol_id, my_obs_input, my_adj_path):
                                st.toast("✅ Sustento enviado exitosamente a Gerencia", icon="🎉")
                                st.rerun()
                            else:
                                st.error("Error al guardar el sustento. Intente nuevamente.")

st.markdown("""
<div style="width: 100%; text-align: center; margin-top: 36px; margin-bottom: 30px; font-size: 13px; font-weight: 600; color: #8A8E97; letter-spacing: 0.8px;">
    Creado por raules v1.0.0
</div>
""", unsafe_allow_html=True)
