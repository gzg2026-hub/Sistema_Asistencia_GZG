import streamlit as st
import pandas as pd
import datetime
import os
import sys
import base64

# Asegurar importaciones del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.database import (
    init_db, obtener_solicitudes_aprobacion, actualizar_estado_aprobacion,
    sincronizar_aprobaciones_desde_asistencia, cambiar_password_usuario, obtener_usuario_by_username,
    crear_token_sesion, validar_token_sesion, eliminar_token_sesion
)
from core.auth import init_auth, is_authenticated, login_user, logout_user, get_current_user, hash_password, verify_password

from PIL import Image

import json

def get_file_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def get_logo_base64():
    """Obtiene el logo oficial transparente de GZG en Base64."""
    for logo_path in ["assets/gzg_logo_transparent.png", "assets/gzg_logo.png"]:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

def get_hero_base64():
    """Obtiene la imagen de portada minera para el login."""
    hero_path = "assets/login_mining_hero.jpg"
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
    avatar_name = str(worker_name).strip().replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={avatar_name}&background=F58220&color=ffffff&size=80&bold=true&rounded=true"

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

# Inicializar Base de Datos y Autenticación
init_db()
init_auth()

# Inyectar metas para icono y PWA
st.markdown(f"""
<head>
    <title>GZG MINERALES</title>
    <meta name="apple-mobile-web-app-title" content="GZG MINERALES">
    <meta name="application-name" content="GZG MINERALES">
    <meta name="theme-color" content="#121418">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="app/static/manifest.json">
    <link rel="manifest" href="data:application/manifest+json;base64,{manifest_b64}">
    <link rel="apple-touch-icon" sizes="180x180" href="app/static/icon-192.png">
    <link rel="apple-touch-icon" sizes="180x180" href="data:image/png;base64,{icon192_b64}">
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
    /* ELIMINAR 100% EL PARPADEO, DESVANECIMIENTO Y OSCURECIMIENTO DE STREAMLIT */
    *,
    *::before,
    *::after {
        transition-property: background-color, border-color, color, fill, stroke !important;
        transition-duration: 0s !important;
    }
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main,
    div[data-testid="stVerticalBlock"],
    div[data-testid="stTabs"],
    div[data-baseweb="tab-panel"],
    div[data-baseweb="tab-list"],
    div[data-baseweb="tab-border"] {
        opacity: 1 !important;
        transition: none !important;
        animation: none !important;
    }
    [data-test-script-state="running"],
    [data-test-script-state="running"] *,
    .stApp[data-test-script-state="running"],
    .stApp[data-test-script-state="running"] *,
    div[data-testid="stAppViewContainer"][data-test-script-state="running"],
    div[data-testid="stAppViewContainer"][data-test-script-state="running"] * {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
        animation: none !important;
    }
    /* Ocultar skeletons, parches y artefactos de carga preliminar */
    [data-testid="stSkeleton"],
    .stSkeleton,
    div[class*="skeleton"],
    div[class*="Skeleton"],
    div[data-testid="stStatusWidget"],
    div[data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        width: 0px !important;
    }
    /* Ocultar Barra Superior de Streamlit Cloud (Stop, Fork, GitHub, Menu, Accesibilidad) */
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

    /* Ocultar Barra Inferior de Streamlit Cloud y Embed (Built with Streamlit / Fullscreen) */
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
    div[class*="StatusWidget"],
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

    /* Fondo oscuro nativo PWA GZG y Habilitación Estricta de Scroll Táctil */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background-color: #121418 !important;
        background: #121418 !important;
        color: #FFFFFF !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important    /* Padding compacto superior e inferior para vista móvil */
    .main .block-container {
        padding: 0.2rem 0.5rem 50px 0.5rem !important;
        max-width: 500px !important;
        margin: 0 auto !important;
        width: 100% !important;
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

    /* =========================================================================
       PUNTO 1: ÍCONOS PUROS NATIVOS EN LOS INPUTS DE LOGIN (USUARIO Y CONTRASEÑA)
       Anclados directamente a input[aria-label="Usuario"] e input[aria-label="Contraseña"]
       ========================================================================= */
    /* Input 1: Usuario (Ícono Personita 👤) */
    input[aria-label="Usuario"],
    input[aria-label="Usuario"]:focus {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%239A9EA7'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 14px center !important;
        background-size: 18px 18px !important;
        background-color: #1A1D24 !important;
        padding-left: 44px !important;
        text-align: left !important;
        color: #FFFFFF !important;
        font-size: 15px !important;
    }

    /* Input 2: Contraseña (Ícono Candadito 🔒) */
    input[aria-label="Contraseña"],
    input[aria-label="Contraseña"]:focus {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%239A9EA7'%3E%3Cpath d='M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 14px center !important;
        background-size: 18px 18px !important;
        background-color: #1A1D24 !important;
        padding-left: 44px !important;
        text-align: left !important;
        color: #FFFFFF !important;
        font-size: 15px !important;
    }

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

    /* Badges de Estado */
    .badge-approved {
        background-color: rgba(39, 174, 96, 0.2);
        color: #27AE60;
        border: 1px solid #27AE60;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
    }
    .badge-rejected {
        background-color: rgba(231, 76, 60, 0.2);
        color: #E74C3C;
        border: 1px solid #E74C3C;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
    }
    .badge-pending {
        background-color: rgba(243, 156, 18, 0.2);
        color: #F39C12;
        border: 1px solid #F39C12;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
    }

    /* Botones táctiles */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 44px !important;
        touch-action: manipulation !important;
    }

    /* PUNTO 4/5: Botón Rechazar — Rojo Carmesí Sólido con Texto Blanco */
    div[data-testid="column"]:nth-of-type(1) button[data-testid="baseButton-secondary"],
    div[data-testid="column"]:first-child button[data-testid="baseButton-secondary"],
    div[data-testid="column"]:nth-child(1) button[kind="secondary"] {
        background: linear-gradient(135deg, #C0392B 0%, #962D22 100%) !important;
        background-color: #C0392B !important;
        border: 1px solid #E74C3C !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(192, 57, 43, 0.35) !important;
    }
    div[data-testid="column"]:nth-of-type(1) button[data-testid="baseButton-secondary"] p,
    div[data-testid="column"]:first-child button[data-testid="baseButton-secondary"] p,
    div[data-testid="column"]:nth-of-type(1) button[data-testid="baseButton-secondary"] span,
    div[data-testid="column"]:first-child button[data-testid="baseButton-secondary"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    div[data-testid="column"]:nth-of-type(1) button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="column"]:first-child button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #D9383A 0%, #B02A2B 100%) !important;
        background-color: #D9383A !important;
        border-color: #FF5A5A !important;
        color: #FFFFFF !important;
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
# AUTO-LOGIN PERSISTENTE SI "RECORDARME" ESTÁ ACTIVO
# ---------------------------------------------------------
if not is_authenticated():
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

# ---------------------------------------------------------
# PANTALLA DE LOGIN MÓVIL CON FONDO MINERO GZG CORPORATIVO
# ---------------------------------------------------------
if not is_authenticated():
    # Inyectar fondo minero nítido y luminoso en stAppViewContainer
    if hero_b64:
        st.markdown(f"""
<style>
.stApp,
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(180deg, rgba(14, 16, 20, 0.15) 0%, rgba(14, 16, 20, 0.35) 45%, #0E1014 92%), url("data:image/jpeg;base64,{hero_b64}") no-repeat center top !important;
    background-size: cover !important;
    background-attachment: fixed !important;
}}
[data-testid="stMain"], .main, .block-container, div[data-testid="stVerticalBlock"] {{
    background-color: transparent !important;
}}
</style>
""", unsafe_allow_html=True)


    # PUNTO 4: Encabezado de Login Más Proporcionado (Logo 72px, Título 26px, Subtítulo 11px)
    st.markdown(f"""
<div style="text-align: center; padding: 6px 0 6px 0;">
    <div style="margin-bottom: 6px;">
        <img src="data:image/png;base64,{logo_b64}" style="height: 72px; object-fit: contain; filter: drop-shadow(0 6px 18px rgba(0,0,0,0.65));">
    </div>
    <div style="font-size: 26px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; line-height: 1.1; margin-bottom: 4px;">
        <span style="color: #FFFFFF;">GZG</span> <span style="color: #F58220;">MINERALES</span>
    </div>
    <div style="font-size: 11px; font-weight: 700; color: #E0E2EC; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 16px; opacity: 0.95;">
        APLICACION MOVIL PARA APROBACIONES
    </div>
    <div style="text-align: left; margin-top: 4px; margin-bottom: 10px;">
        <div style="font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">Bienvenido</div>
        <div style="font-size: 13px; color: #9A9EA7;">Inicia sesión para continuar</div>
    </div>
</div>
""", unsafe_allow_html=True)
    
    with st.form("form_login_mobile"):
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
<div style="text-align: center; font-size: 11px; font-weight: 600; color: #9A9EA7; margin: 18px 0 25px 0; letter-spacing: 0.8px;">
Creado por raules v1.0.0
</div>
""", unsafe_allow_html=True)
    
    st.stop()

# ---------------------------------------------------------
# APLICACIÓN MÓVIL PWA PRINCIPAL (USUARIOS AUTENTICADOS)
# ---------------------------------------------------------
current_user = get_current_user()
username = current_user.get('username', 'Supervisor') if current_user else 'Supervisor'
rol = current_user.get('rol', 'SUPERVISOR') if current_user else 'SUPERVISOR'

# PUNTO 4: Cabecera Central Corporativa GZG en Dashboard — Proporcionada y Elegante
st.markdown(f"""
<div style="text-align: center; padding: 4px 0 4px 0;">
    <div style="margin-bottom: 4px;">
        <img src="data:image/png;base64,{logo_b64}" style="height: 58px; object-fit: contain; filter: drop-shadow(0 4px 14px rgba(0,0,0,0.55));">
    </div>
    <div style="font-size: 21px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; line-height: 1.1; margin-bottom: 2px;">
        <span style="color: #FFFFFF;">GZG</span> <span style="color: #F58220;">MINERALES</span>
    </div>
    <div style="font-size: 10px; font-weight: 700; color: #E0E2EC; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; opacity: 0.95;">
        CONTROL DE ASISTENCIA
    </div>
</div>
""", unsafe_allow_html=True)


# Fila de Usuario y Acciones Rápidas
col_user, col_actions = st.columns([1.6, 1.4])
with col_user:
    st.markdown(f"<div style='padding-top: 6px; font-size: 13px; font-weight: 600; color: #FFFFFF;'>👋 <b>Hola, {username}</b> <span style='color: #9A9EA7; font-size: 11px;'>({rol})</span></div>", unsafe_allow_html=True)
with col_actions:
    c_act1, c_act2 = st.columns(2)
    with c_act1:
        with st.popover("🔑 Clave"):
            st.markdown("##### 🔑 Cambiar Contraseña")
            with st.form("form_header_change_pw"):
                p_act_h = st.text_input("Contraseña Actual", type="password")
                p_nue_h = st.text_input("Nueva Contraseña", type="password")
                p_cnf_h = st.text_input("Confirmar Nueva Contraseña", type="password")
                btn_h_pw = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
                if btn_h_pw:
                    if current_user and not verify_password(p_act_h, current_user.get('password_hash', '')):
                        st.error("La contraseña actual es incorrecta.")
                    elif not p_nue_h or len(p_nue_h) < 4:
                        st.warning("Debe tener al menos 4 caracteres.")
                    elif p_nue_h != p_cnf_h:
                        st.error("Las contraseñas no coinciden.")
                    else:
                        new_h = hash_password(p_nue_h)
                        if cambiar_password_usuario(username, new_h):
                            st.toast("🎉 ¡Contraseña actualizada!", icon="🔑")
                            st.success("Contraseña modificada exitosamente.")
                            st.rerun()
                        else:
                            st.error("Error al actualizar la contraseña.")
    with c_act2:
        if st.button("🚪 Salir", key="btn_logout_mobile", use_container_width=True):
            if "token" in st.query_params:
                eliminar_token_sesion(st.query_params["token"])
                del st.query_params["token"]
            logout_user()
            st.rerun()



# Cargar data de aprobaciones directamente de SQLite sin bucles
df_all_raw = obtener_solicitudes_aprobacion('TODAS')

# PUNTO 7: Filtrado por bandeja personal del usuario autenticado
if rol not in ('ADMINISTRACION', 'ADMIN') and 'aprobador_n1' in df_all_raw.columns:
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
# TAB 1: PENDIENTES DE APROBACIÓN (EVALUACIÓN POR NIVEL)
# ---------------------------------------------------------
with tab_pendientes:
    u_lower = username.lower().strip()
    if rol in ('ADMINISTRACION', 'ADMIN'):
        df_pendientes = df_all[df_all['estado'] == 'PENDIENTE'].copy()
        df_aprobadas_mes = df_all[df_all['estado'] == 'APROBADO'].copy()
    else:
        # Pendiente para el usuario según su nivel asignado (N1 o N2):
        is_pend_for_me = (
            (df_all['aprobador_n1'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n1'] == 'PENDIENTE')
        ) | (
            (df_all['aprobador_n2'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n2'] == 'PENDIENTE') & (df_all['estado_n1'] != 'RECHAZADO')
        )
        df_pendientes = df_all[is_pend_for_me & (df_all['estado'] != 'RECHAZADO')].copy()
        
        # Aprobada por el usuario o resuelta:
        is_app_by_me = (
            (df_all['aprobador_n1'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n1'] == 'APROBADO')
        ) | (
            (df_all['aprobador_n2'].fillna('').str.lower().str.strip() == u_lower) & (df_all['estado_n2'] == 'APROBADO')
        ) | (df_all['estado'] == 'APROBADO')
        df_aprobadas_mes = df_all[is_app_by_me].copy()

    
    col_kpi1, col_kpi2 = st.columns(2)
    with col_kpi1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F58220 0%, #D35400 100%); border-radius: 12px; padding: 12px; text-align: center;">
            <div style="font-size: 24px; font-weight: 800; color: #FFF;">{len(df_pendientes)}</div>
            <div style="font-size: 11px; color: #FFF;">Pendientes</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"""
        <div style="background: #1D212A; border: 1px solid #2A2F3D; border-radius: 12px; padding: 12px; text-align: center;">
            <div style="font-size: 24px; font-weight: 800; color: #F58220;">{len(df_aprobadas_mes)}</div>
            <div style="font-size: 11px; color: #9A9EA7;">Aprobadas este mes</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if df_pendientes.empty:
        st.info("🎉 ¡Excelente! No tienes solicitudes pendientes en este momento.")
    else:
        for idx, row in df_pendientes.iterrows():
            sol_id = row['id']
            worker_name = f"{row.get('nombres', '')} {row.get('apellidos', '')}".title()
            cargo = row.get('cargo', 'Operativo')
            fecha_sol = row.get('fecha', '')
            he_hhmm = row.get('horas_extras_hhmm', '0h 00m')
            exceso_hhmm = row.get('exceso_jornada_hhmm', '0h 00m')
            
            avatar_url = get_worker_avatar_url(row.get('dni'), worker_name)
            
            with st.expander(f"👤 **{worker_name}** ({fecha_sol})", expanded=True):
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; margin: 6px 0 12px 0;">
                    <img src="{avatar_url}" style="width: 42px; height: 42px; border-radius: 50%; border: 2px solid #F58220; object-fit: cover; flex-shrink: 0;" />
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">{worker_name}</div>
                        <div style="font-size: 12px; color: #9A9EA7;">{cargo} ({fecha_sol})</div>
                    </div>
                </div>

                - 🕒 **Entrada**: `{row.get('entrada', '-')}` | **Salida**: `{row.get('salida', '-')}`
                - ⏱️ **Jornada trabajada**: {row.get('jornada_trabajada_hhmm', '-')}
                - ⏰ **Horas extras**: <b style="color: #F58220;">{he_hhmm}</b>
                - ⚠️ **Exceso de jornada**: <b style="color: #E67E22;">{exceso_hhmm}</b>
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
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
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

                        actualizar_estado_aprobacion(sol_id, 'RECHAZADO', username, comentario_aprobador)
                        st.success(f"Rechazado: {worker_name}")
                        st.rerun()
                with c_btn2:
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

                        actualizar_estado_aprobacion(sol_id, 'APROBADO', username, comentario_aprobador)
                        st.success(f"Aprobado: {worker_name}")
                        st.rerun()

# ---------------------------------------------------------
# TAB 2: HISTORIAL DE APROBACIONES
# ---------------------------------------------------------
with tab_historial:
    filtro_estado = st.radio("Estado:", ["TODAS", "APROBADAS", "RECHAZADAS"], horizontal=True, key="rad_m_hist")
    
    df_hist = df_all.copy()
    if filtro_estado == "APROBADAS":
        df_hist = df_hist[df_hist['estado'] == 'APROBADO']
    elif filtro_estado == "RECHAZADAS":
        df_hist = df_hist[df_hist['estado'] == 'RECHAZADO']
        
    if df_hist.empty:
        st.info("No hay registros en el historial para este filtro.")
    else:
        cards_list = []
        for idx, row in df_hist.iterrows():
            worker_name = f"{row.get('nombres', '')} {row.get('apellidos', '')}".title()
            cargo = row.get('cargo', '')
            fecha_sol = row.get('fecha', '')
            estado = row.get('estado', 'PENDIENTE')
            he_hhmm = row.get('horas_extras_hhmm', '0h 00m')
            exceso_hhmm = row.get('exceso_jornada_hhmm', '0h 00m')
            aprobador = row.get('aprobado_por', 'Sistema')
            
            badge_html = f'<span class="badge-approved">APROBADO</span>' if estado == 'APROBADO' else (
                f'<span class="badge-rejected">RECHAZADO</span>' if estado == 'RECHAZADO' else f'<span class="badge-pending">PENDIENTE</span>'
            )
            
            cards_list.append(f"""
            <div class="approval-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="worker-name">{worker_name}</div>
                    <div>{badge_html}</div>
                </div>
                <div class="worker-role">{cargo} ({fecha_sol})</div>
                <hr style="border-color: #2A2F3D; margin: 8px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <div>⏰ H.E.: <b style="color: #F58220;">{he_hhmm}</b></div>
                    <div>⚠️ Exceso: <b style="color: #E67E22;">{exceso_hhmm}</b></div>
                </div>
                <div style="font-size: 10px; color: #6C727F; margin-top: 6px;">Por: {aprobador}</div>
            </div>
            """)
        st.markdown("".join(cards_list), unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: DASHBOARD DE ESTADÍSTICAS
# ---------------------------------------------------------
with tab_dashboard:
    n_aprob = len(df_all[df_all['estado'] == 'APROBADO'])
    n_rech = len(df_all[df_all['estado'] == 'RECHAZADO'])
    n_pend = len(df_all[df_all['estado'] == 'PENDIENTE'])
    
    st.metric("HE Aprobadas", f"{n_aprob}")
    st.metric("Excesos Aprobados", f"{n_aprob}")
    st.metric("Pendientes", f"{n_pend}")
    
    if len(df_all) > 0:
        chart_df = pd.DataFrame({
            'Estado': ['Aprobadas', 'Rechazadas', 'Pendientes'],
            'Cantidad': [n_aprob, n_rech, n_pend]
        })
        st.bar_chart(chart_df.set_index('Estado'))

st.markdown("""
<div style="text-align: center; font-size: 12px; font-weight: 600; color: #9A9EA7; margin: 40px 0 60px 0; letter-spacing: 0.8px;">
Creado por raules v1.0.0
</div>
""", unsafe_allow_html=True)
