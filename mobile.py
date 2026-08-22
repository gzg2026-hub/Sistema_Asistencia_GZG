import streamlit as st
import pandas as pd
import datetime
import os
import sys

# Asegurar importaciones del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.database import (
    init_db, obtener_solicitudes_aprobacion, actualizar_estado_aprobacion,
    sincronizar_aprobaciones_desde_asistencia
)
from core.auth import init_auth, is_authenticated, login_user, logout_user, get_current_user

import base64

# Configuración de página 100% enfocada en Celular (Centrado sin Sidebar)
st.set_page_config(
    page_title="GZG Minerales - Aprobaciones Móvil",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inicializar Base de Datos y Autenticación
init_db()
init_auth()

def get_logo_base64():
    """Obtiene el logo oficial transparente de GZG en Base64."""
    for logo_path in ["assets/gzg_logo_transparent.png", "assets/gzg_logo.png"]:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_logo_base64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 45px; margin-right: 10px; vertical-align: middle;">' if logo_b64 else ''

# CSS TOTALMENTE AISLADO PARA CELULARES (Hides all desktop elements)
st.markdown("""
<style>
    /* Ocultar completamente Sidebar, Header de Streamlit y Footers */
    section[data-testid="stSidebar"],
    div[data-testid="stSidebarCollapsedControl"],
    header[data-testid="stHeader"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    div[data-testid="stToolbar"],
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
    div[data-baseweb="tab-list"] button {
        flex: 1 1 auto !important;
        font-size: 13px !important;
        padding: 8px 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PANTALLA DE LOGIN MÓVIL (SI NO ESTÁ AUTENTICADO)
# ---------------------------------------------------------
if not is_authenticated():
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div style="display: inline-flex; align-items: center; justify-content: center;">
            {logo_html}
            <div>
                <span class="gzg-logo-text">GZG</span> <span class="gzg-logo-text gzg-orange">MINERALES</span>
                <div style="font-size: 11px; color: #9A9EA7; letter-spacing: 1px;">APLICACIÓN MÓVIL DE APROBACIONES</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_login_mobile"):
        st.markdown("#### 🔐 Iniciar Sesión")
        u_name = st.text_input("Usuario", placeholder="ej. admin o supervisor")
        u_pass = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        btn_login = st.form_submit_button("🔑 INGRESAR A LA APP", type="primary", use_container_width=True)
        if btn_login:
            if u_name and u_pass:
                success, msg = login_user(u_name, u_pass)
                if success:
                    st.success("Acceso concedido")
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Ingresa usuario y contraseña")
    st.stop()

# ---------------------------------------------------------
# APLICACIÓN MÓVIL PWA PRINCIPAL (USUARIOS AUTENTICADOS)
# ---------------------------------------------------------
current_user = get_current_user()
username = current_user.get('username', 'Supervisor') if current_user else 'Supervisor'
rol = current_user.get('rol', 'SUPERVISOR') if current_user else 'SUPERVISOR'

# Cabecera Móvil GZG con Logo Corporativo Oficial
col_head1, col_head2 = st.columns([3.5, 1])
with col_head1:
    st.markdown(f"""
    <div style="display: flex; align-items: center;">
        {logo_html}
        <div>
            <span class="gzg-logo-text" style="font-size: 18px;">GZG</span> <span class="gzg-logo-text gzg-orange" style="font-size: 18px;">MINERALES</span>
            <div style="font-size: 10px; color: #9A9EA7;">CONTROL DE ASISTENCIA Y APROBACIONES</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_head2:
    if st.button("🚪 Salir", key="btn_logout_mobile", use_container_width=True):
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
            obs_trabajador = row.get('observacion_trabajador', '')
            motivo = row.get('motivo', 'Trabajo operativo adicional en turno')
            
            with st.expander(f"👤 **{worker_name}** ({fecha_sol})", expanded=True):
                st.markdown(f"""
                - 💼 **Cargo**: {cargo}
                - 🕒 **Entrada**: `{row.get('entrada', '-')}` | **Salida**: `{row.get('salida', '-')}`
                - ⏱️ **Jornada trabajada**: {row.get('jornada_trabajada_hhmm', '-')}
                - ⏰ **Horas extras**: <b style="color: #F58220;">{he_hhmm}</b>
                - ⚠️ **Exceso de jornada**: <b style="color: #E67E22;">{exceso_hhmm}</b>
                - 📝 **Motivo**: {motivo}
                """, unsafe_allow_html=True)
                
                if obs_trabajador:
                    st.info(f"💬 **Observación**: {obs_trabajador}")
                    
                comentario = st.text_input(f"Comentario opcional ({worker_name})", key=f"m_com_{sol_id}", placeholder="Escribe un comentario...")
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("❌ RECHAZAR", key=f"m_rej_{sol_id}", use_container_width=True):
                        actualizar_estado_aprobacion(sol_id, 'RECHAZADO', username, comentario)
                        st.success(f"Rechazado: {worker_name}")
                        st.rerun()
                with c_btn2:
                    if st.button("✅ APROBAR", key=f"m_app_{sol_id}", type="primary", use_container_width=True):
                        actualizar_estado_aprobacion(sol_id, 'APROBADO', username, comentario)
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
            
            st.markdown(f"""
            <div class="approval-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="worker-name">{worker_name}</div>
                    <div>{badge_html}</div>
                </div>
                <div class="worker-role">{cargo} | {fecha_sol}</div>
                <hr style="border-color: #2A2F3D; margin: 8px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <div>⏰ HE: <b style="color: #F58220;">{he_hhmm}</b></div>
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
