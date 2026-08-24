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
    sincronizar_aprobaciones_desde_asistencia, cambiar_password_usuario, obtener_usuario_by_username
)
from core.auth import init_auth, is_authenticated, login_user, logout_user, get_current_user, hash_password, verify_password

from PIL import Image

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
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 45px; margin-right: 10px; vertical-align: middle;">' if logo_b64 else ''
logo_icon = Image.open("assets/gzg_logo.png") if os.path.exists("assets/gzg_logo.png") else "📱"

# Configuración de página 100% enfocada en Celular (Centrado sin Sidebar)
st.set_page_config(
    page_title="GZG Minerales - Aprobaciones",
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
    <meta name="apple-mobile-web-app-title" content="GZG Minerales">
    <meta name="application-name" content="GZG Minerales">
    <meta name="theme-color" content="#F58220">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="data:image/png;base64,{logo_b64}">
    <link rel="icon" type="image/png" href="data:image/png;base64,{logo_b64}">
    <link rel="shortcut icon" href="data:image/png;base64,{logo_b64}">
</head>
""", unsafe_allow_html=True)

# CSS TOTALMENTE AISLADO PARA CELULARES (Hides all desktop elements & prevents flickering)
st.markdown("""
<style>
    /* Desactivar parpadeo, oscurecimiento y animaciones de recarga de Streamlit */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main,
    div[data-testid="stVerticalBlock"] {
        opacity: 1 !important;
        transition: none !important;
        animation: none !important;
    }
    .stApp[data-test-script-state="running"] {
        opacity: 1 !important;
    }
    div[data-testid="stStatusWidget"],
    div[data-testid="stDecoration"],
    div[data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Ocultar completamente Sidebar, Header de Streamlit y Footers */
    section[data-testid="stSidebar"],
    div[data-testid="stSidebarCollapsedControl"],
    header[data-testid="stHeader"],
    footer,
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        height: 0px !important;
    }

    /* Fondo oscuro nativo PWA GZG */
    .stApp, [data-testid="stMain"] {
        background-color: #121418 !important;
        background: #121418 !important;
        color: #FFFFFF !important;
    }

    /* Ajustar el contenedor principal al 100% de la pantalla del celular sin márgenes desbordados */
    .main .block-container {
        padding: 0.75rem 0.5rem !important;
        max-width: 500px !important;
        margin: 0 auto !important;
        width: 100% !important;
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
    }

    /* Estilo de pestañas superiores en celular */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        gap: 4px !important;
        margin-bottom: 12px !important;
    }
    /* Bordes sutiles 1px idénticos a los botones secundarios, cards y uploader */
    div[data-testid="stForm"],
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
    .stTextInput input, input[type="text"], input[type="password"] {
        color: #FFFFFF !important;
    }

    /* Ocultar permanentemente la instrucción "Press Enter to submit form" */
    [data-testid="InputInstructions"], div[data-testid="InputInstructions"], .stInputInstructions {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        opacity: 0 !important;
    }
    div[data-baseweb="input"] input {
        font-size: 15px !important;
        padding: 10px 14px !important;
    }
    div[data-baseweb="input"] input::placeholder {
        font-size: 18px !important;
        opacity: 0.8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# AUTO-LOGIN SI "RECORDARME" ESTÁ ACTIVO
# ---------------------------------------------------------
if not is_authenticated():
    saved_user = st.query_params.get("user", "")
    if saved_user and f"auth_token_{saved_user}" in st.session_state:
        # Re-autenticar automáticamente
        st.session_state["authenticated"] = True
        st.session_state["current_user"] = st.session_state[f"auth_token_{saved_user}"]

# ---------------------------------------------------------
# PANTALLA DE LOGIN MÓVIL ESTILO GZG CORPORATIVO
# ---------------------------------------------------------
if not is_authenticated():
    hero_html = f'''
    <div style="width: 100%; border-radius: 16px; overflow: hidden; margin: 12px 0 16px 0; box-shadow: 0 8px 24px rgba(0,0,0,0.6); border: 1px solid #2A2F3D;">
        <img src="data:image/jpeg;base64,{hero_b64}" style="width: 100%; height: 165px; object-fit: cover; display: block;">
    </div>
    ''' if hero_b64 else ''

    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div style="margin-bottom: 8px;">
            <img src="data:image/png;base64,{logo_b64}" style="height: 85px; object-fit: contain; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.5));">
        </div>
        <div style="font-size: 26px; font-weight: 900; color: #F58220; letter-spacing: 2px; text-transform: uppercase; line-height: 1.1;">
            MINERALES
        </div>
        <div style="font-size: 11px; font-weight: 700; color: #FFFFFF; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 6px; margin-bottom: 8px; opacity: 0.95;">
            APLICACIÓN MÓVIL PARA APROBACIONES
        </div>
        {hero_html}
        <div style="text-align: left; margin-top: 14px; margin-bottom: 8px;">
            <div style="font-size: 24px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">Bienvenido</div>
            <div style="font-size: 13px; color: #9A9EA7;">Inicia sesión para continuar</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_login_mobile"):
        u_name = st.text_input("Usuario", placeholder="👤", label_visibility="collapsed")
        u_pass = st.text_input("Contraseña", type="password", placeholder="🔒", label_visibility="collapsed")
        
        col_rec, _ = st.columns([1.5, 1])
        with col_rec:
            recordarme = st.toggle("Recordarme", value=True, key="chk_recordarme_login")
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        btn_login = st.form_submit_button("INICIAR SESIÓN", type="primary", use_container_width=True)
        if btn_login:
            if u_name and u_pass:
                if login_user(u_name.strip(), u_pass.strip()):
                    if recordarme:
                        st.query_params["user"] = u_name.strip().lower()
                        st.session_state[f"auth_token_{u_name.strip().lower()}"] = get_current_user()
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
            else:
                st.warning("Por favor ingresa tu usuario y contraseña.")
    
    st.markdown("""
    <div style="text-align: center; font-size: 11px; color: #5A5E6B; margin-top: 25px; letter-spacing: 1px;">
        v1.0.0
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# ---------------------------------------------------------
# APLICACIÓN MÓVIL PWA PRINCIPAL (USUARIOS AUTENTICADOS)
# ---------------------------------------------------------
current_user = get_current_user()
username = current_user.get('username', 'Supervisor') if current_user else 'Supervisor'
rol = current_user.get('rol', 'SUPERVISOR') if current_user else 'SUPERVISOR'

# Cabecera Móvil GZG con Renderizado Inmediato
col_head1, col_head2, col_head3 = st.columns([2.3, 1.2, 1.1])
with col_head1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; padding: 4px 0;">
        {logo_html}
        <div>
            <span class="gzg-logo-text" style="font-size: 16px;">GZG</span> <span class="gzg-logo-text gzg-orange" style="font-size: 16px;">MINERALES</span>
            <div style="font-size: 9px; color: #9A9EA7;">CONTROL DE ASISTENCIA</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_head2:
    with st.popover("🔑 Mi Clave"):
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
with col_head3:
    if st.button("🚪 Salir", key="btn_logout_mobile", use_container_width=True):
        if "user" in st.query_params:
            del st.query_params["user"]
        logout_user()
        st.rerun()

st.write(f"👋 **Hola, {username}** ({rol})")

# Cargar data de aprobaciones de forma eficiente (sin bucles de sincronización)
if 'aprobaciones_synced' not in st.session_state:
    sincronizar_aprobaciones_desde_asistencia()
    st.session_state['aprobaciones_synced'] = True

df_all = obtener_solicitudes_aprobacion('TODAS')

# 3 Pestañas Móviles PWA
tab_pendientes, tab_historial, tab_dashboard = st.tabs([
    "📋 Pendientes", "📜 Historial", "📊 Dashboard"
])

# ---------------------------------------------------------
# TAB 1: PENDIENTES DE APROBACIÓN
# ---------------------------------------------------------
with tab_pendientes:
    df_pendientes = df_all[df_all['estado'] == 'PENDIENTE']
    df_aprobadas_mes = df_all[df_all['estado'] == 'APROBADO']
    
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
                    "📷 Adjuntar Foto / Imagen de Sustento (opcional)",
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
        root_dir = os.path.dirname(os.path.abspath(__file__))
        for idx, row in df_hist.iterrows():
            worker_name = f"{row.get('nombres', '')} {row.get('apellidos', '')}".title()
            cargo = row.get('cargo', '')
            fecha_sol = row.get('fecha', '')
            estado = row.get('estado', 'PENDIENTE')
            he_hhmm = row.get('horas_extras_hhmm', '0h 00m')
            exceso_hhmm = row.get('exceso_jornada_hhmm', '0h 00m')
            aprobador = row.get('aprobado_por', 'Sistema')
            c_aprob = row.get('comentario_n1', '') or row.get('comentario_n2', '')
            adjunto = row.get('adjuntos', '')
            
            badge_html = f'<span class="badge-approved">APROBADO</span>' if estado == 'APROBADO' else (
                f'<span class="badge-rejected">RECHAZADO</span>' if estado == 'RECHAZADO' else f'<span class="badge-pending">PENDIENTE</span>'
            )
            
            st.markdown(f"""
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
            """, unsafe_allow_html=True)

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
