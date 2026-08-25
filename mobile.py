import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import time
import os
import sys
import base64

def signal_ready():
    """Notifica a index.html (la página padre de la PWA) que el contenido ya se renderizó."""
    try:
        components.html(
            "<script>try{window.top.postMessage({type: 'gzg:ready'}, '*');}catch(e){}</script>",
            height=0, width=0
        )
    except Exception:
        pass

# Asegurar importaciones del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.database import (
    init_db, obtener_solicitudes_aprobacion, actualizar_estado_aprobacion,
    sincronizar_aprobaciones_desde_asistencia, sincronizar_aprobaciones_con_gdrive,
    regenerar_aprobaciones_excel,
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
        margin-bottom: 12px !important;
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

# Formatear nombre corto para el saludo (Primer Nombre y Apellido)
def get_user_display_name(u_dict, u_name):
    if not u_dict:
        return u_name.title()
    u = u_dict.get('username', u_name).lower().strip()
    if u == 'jdelariva':
        return "Javier De La Riva"
    if u == 'jagreda':
        return "Jhon Ágreda"
    if u == 'jalva':
        return "Jhon Alva"
    if u == 'jhuayama':
        return "Josmell Huayama"
    if u == 'msanchez':
        return "Manuel Sánchez"
    if u == 'admin':
        return "admin"
    nombre_comp = u_dict.get('nombre_completo', '')
    if nombre_comp:
        partes = nombre_comp.strip().split()
        if len(partes) >= 2:
            return f"{partes[0]} {partes[-1]}".title()
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

<div style="background: rgba(26, 29, 36, 0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 7px 12px; margin-top: 12px; margin-bottom: -4px; display: flex; justify-content: space-between; align-items: center;">
    <div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">
        Hola, {nombre_saludo} 👋
    </div>
    <div style="font-size: 10px; font-weight: 700; color: #F58220; background: rgba(245, 130, 32, 0.15); border: 1px solid rgba(245, 130, 32, 0.3); border-radius: 6px; padding: 2px 8px; letter-spacing: 0.5px; text-transform: uppercase;">
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

# 2 Botones Nativos Gemelos Simétricos (50% Cambiar clave a la izquierda / 50% Salir a la derecha)
col_b1, col_b2 = st.columns(2)
with col_b1:
    st.button("🔑 Cambiar clave", key="btn_toggle_change_pw", on_click=callback_toggle_pw, use_container_width=True)

with col_b2:
    st.button("🚪 Salir", key="btn_logout_mobile", on_click=callback_logout, use_container_width=True)

# Formulario desplegable para cambiar contraseña al pulsar el botón Clave
if st.session_state.get("show_change_pw_box", False):
    with st.expander("🔑 Cambiar mi Contraseña", expanded=True):
        st.markdown("""
        <div style="background: rgba(245, 130, 32, 0.08); border: 1px solid rgba(245, 130, 32, 0.25); border-radius: 8px; padding: 6px 10px; margin-bottom: 8px; font-size: 11px; color: #D1D5DB;">
            💡 <b>Sugerencia:</b> La nueva contraseña debe tener <b>6 o más caracteres</b> (letras, números o símbolos).
        </div>
        """, unsafe_allow_html=True)
        with st.form("form_header_change_pw"):
            p_act_h = st.text_input("Contraseña Actual", type="password")
            p_nue_h = st.text_input("Nueva Contraseña", type="password", placeholder="Mínimo 6 caracteres", help="Debe tener al menos 6 caracteres")
            p_cnf_h = st.text_input("Confirmar Nueva Contraseña", type="password", placeholder="Repite la nueva contraseña")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                btn_h_pw = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
            with col_f2:
                btn_h_close = st.form_submit_button("✖ Cerrar", use_container_width=True)
            
            if btn_h_close:
                st.session_state["show_change_pw_box"] = False
                st.rerun()
            if btn_h_pw:
                db_u = obtener_usuario_by_username(username)
                if not db_u or not verify_password(p_act_h.strip(), db_u.get('password_hash', '')):
                    st.error("La contraseña actual es incorrecta.")
                elif not p_nue_h or len(p_nue_h.strip()) < 6:
                    st.warning("⚠️ La nueva contraseña debe tener al menos 6 caracteres.")
                elif p_nue_h.strip() != p_cnf_h.strip():
                    st.error("Las contraseñas no coinciden.")
                else:
                    new_h = hash_password(p_nue_h.strip())
                    if cambiar_password_usuario(username, new_h):
                        eliminar_token_sesion(username=username)
                        st.toast("🎉 ¡Contraseña actualizada!", icon="🔑")
                        st.success("Contraseña modificada exitosamente.")
                        st.session_state["show_change_pw_box"] = False
                        st.rerun()
                    else:
                        st.error("Error al actualizar la contraseña.")




# Sincronizar estado persistente de aprobaciones con Google Drive / Excel
ahora_ts = time.time()
if "gdrive_clean_pushed" not in st.session_state:
    try:
        regenerar_aprobaciones_excel()
    except Exception:
        pass
    st.session_state["gdrive_clean_pushed"] = True
    st.session_state["last_drive_sync"] = ahora_ts
elif (ahora_ts - st.session_state.get("last_drive_sync", 0)) > 10:
    sincronizar_aprobaciones_con_gdrive()
    st.session_state["last_drive_sync"] = ahora_ts

# Cargar data de aprobaciones directamente de SQLite sin bucles
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


# 3 Pestañas Móviles PWA
tab_pendientes, tab_historial, tab_dashboard = st.tabs([
    "📋 Pendientes", "📜 Historial", "📊 Dashboard"
])

# ---------------------------------------------------------
# CÁLCULO UNIFICADO Y CORRELACIONADO DE BANDEJAS POR ROL
# ---------------------------------------------------------
u_lower = username.lower().strip()
if rol in ('ADMINISTRADOR', 'ADMINISTRACION', 'ADMIN'):
    df_pendientes = df_all[df_all['estado'] == 'PENDIENTE'].copy()
    df_aprobadas_mes = df_all[df_all['estado'] == 'APROBADO'].copy()
    df_rechazadas_mes = df_all[df_all['estado'] == 'RECHAZADO'].copy()
else:
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

# ---------------------------------------------------------
# TAB 1: PENDIENTES DE APROBACIÓN (EVALUACIÓN POR NIVEL)
# ---------------------------------------------------------
with tab_pendientes:
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
            he_hhmm = row.get('horas_extras_hhmm', '00:00')
            exceso_hhmm = row.get('exceso_jornada_hhmm', '00:00')
            avatar_url = get_worker_avatar_url(row.get('dni'), worker_name)
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
                    <div>⏱️ <strong style="color: #FFFFFF;">Jornada trabajada:</strong> {row.get('jornada_trabajada_hhmm', '-')}</div>
                    <div>⏰ <strong style="color: #FFFFFF;">Horas extras:</strong> <b style="color: #F58220;">{he_hhmm}</b></div>
                    <div>⚠️ <strong style="color: #FFFFFF;">Exceso de jornada:</strong> <b style="color: #E67E22;">{exceso_hhmm}</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                comentario_aprobador = st.text_input(
                    "✍️ Comentario del Aprobador",
                    key=f"m_com_{sol_id}",
                    placeholder=""
                )
                
                uploaded_file = st.file_uploader(
                    "📷 Adjuntar Foto",
                    type=["png", "jpg", "jpeg"],
                    key=f"m_file_{sol_id}"
                )
                
                # 2 Botones Gemelos Simétricos 50% / 50% en Fila Horizontal
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("❌ RECHAZAR", key=f"m_rej_{sol_id}", use_container_width=True):
                        adjunto_rel_path = None
                        if uploaded_file is not None:
                            root_dir = os.path.dirname(os.path.abspath(__file__))
                            adj_dir = os.path.join(root_dir, "downloads", "adjuntos_aprobaciones")
                            os.makedirs(adj_dir, exist_ok=True)
                            fname = f"solic_{sol_id}_{uploaded_file.name}"
                            fpath = os.path.join(adj_dir, fname)
                            with open(fpath, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            adjunto_rel_path = os.path.join("downloads", "adjuntos_aprobaciones", fname)

                        with st.spinner("Sincronizando con Google Drive..."):
                            actualizar_estado_aprobacion(sol_id, 'RECHAZADO', username, comentario_aprobador, adjunto_rel_path)
                        st.toast(f"❌ Rechazado: {worker_name}", icon="ℹ️")
                        st.rerun()

                with col_act2:
                    if st.button("✅ APROBAR", key=f"m_app_{sol_id}", type="primary", use_container_width=True):
                        adjunto_rel_path = None
                        if uploaded_file is not None:
                            root_dir = os.path.dirname(os.path.abspath(__file__))
                            adj_dir = os.path.join(root_dir, "downloads", "adjuntos_aprobaciones")
                            os.makedirs(adj_dir, exist_ok=True)
                            fname = f"solic_{sol_id}_{uploaded_file.name}"
                            fpath = os.path.join(adj_dir, fname)
                            with open(fpath, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            adjunto_rel_path = os.path.join("downloads", "adjuntos_aprobaciones", fname)

                        with st.spinner("Sincronizando con Google Drive..."):
                            actualizar_estado_aprobacion(sol_id, 'APROBADO', username, comentario_aprobador, adjunto_rel_path)
                        st.toast(f"✅ Aprobado: {worker_name}", icon="🎉")
                        st.rerun()

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
        df_hist = df_all.copy()
        
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
            he_hhmm = row.get('horas_extras_hhmm', '0h 00m')
            exceso_hhmm = row.get('exceso_jornada_hhmm', '0h 00m')
            
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
            
            cards_list.append(f"""
            <div class="approval-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; width: 100%;">
                    <div class="worker-name" style="flex: 1 1 auto; min-width: 0; word-break: break-word; line-height: 1.25;">{worker_name}</div>
                    <div style="flex-shrink: 0; white-space: nowrap; padding-top: 1px;">{badge_html}</div>
                </div>
                <div class="worker-role">{cargo} ({fecha_sol})</div>
                <hr style="border-color: #2A2F3D; margin: 8px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <div>⏰ H.E.: <b style="color: #F58220;">{he_hhmm}</b></div>
                    <div>⚠️ Exceso: <b style="color: #E67E22;">{exceso_hhmm}</b></div>
                </div>
                <div style="font-size: 10px; color: #9A9EA7; margin-top: 6px;">{aprob_str}</div>
            </div>
            """)
        st.markdown("".join(cards_list), unsafe_allow_html=True)

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

st.markdown("""
<div style="width: 100%; text-align: center; margin-top: 36px; margin-bottom: 30px; font-size: 13px; font-weight: 600; color: #8A8E97; letter-spacing: 0.8px;">
    Creado por raules v1.0.0
</div>
""", unsafe_allow_html=True)
