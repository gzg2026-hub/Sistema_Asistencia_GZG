import streamlit as st
import pandas as pd
import datetime
from data.database import (
    obtener_solicitudes_aprobacion,
    actualizar_estado_aprobacion,
    actualizar_estado_aprobacion_nivel,
    sincronizar_aprobaciones_desde_asistencia,
    cambiar_password_usuario
)
from core.auth import get_current_user, hash_password, verify_password

def get_worker_avatar_url(dni: str, worker_name: str) -> str:
    if dni:
        dni_clean = str(dni).strip().lstrip('0').zfill(8)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

def render_mobile_approvals():
    """Renderiza el Módulo Móvil PWA de Aprobaciones con el diseño GZG Minerales (Modo Oscuro)."""
    
    # 1. Inyectar CSS personalizado para replicar exactamente las capturas (Dark Mode GZG Mining)
    st.markdown("""
    <style>
    /* Estilos globales Móvil GZG */
    .stApp {
        background-color: #121418 !important;
        color: #FFFFFF !important;
    }
    
    /* Ocultar elementos de escritorio que deforman la vista en celulares */
    @media screen and (max-width: 768px) {
        .header-container {
            display: none !important;
        }
        .main .block-container {
            padding: 0.5rem 0.25rem !important;
            width: 100% !important;
            max-width: 100% !important;
        }
    }
    
    /* Contenedor simulador celular */
    .mobile-header {
        background: linear-gradient(185deg, #1D212A 0%, #121418 100%);
        padding: 15px 20px;
        border-bottom: 1px solid #2A2F3D;
        margin-bottom: 20px;
        border-radius: 12px;
        width: 100% !important;
    }
    
    .gzg-logo-text {
        font-family: 'Arial Black', sans-serif;
        font-size: 24px;
        letter-spacing: 2px;
        color: #FFFFFF;
    }
    .gzg-orange {
        color: #F58220 !important;
    }
    
    /* KPI Cards superiores */
    .kpi-card-pending {
        background: linear-gradient(135deg, #F58220 0%, #D35400 100%);
        border-radius: 14px;
        padding: 16px;
        color: #FFFFFF;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(245, 130, 32, 0.25);
    }
    
    .kpi-card-alert {
        background: #1D212A;
        border: 1px solid #2A2F3D;
        border-radius: 14px;
        padding: 16px;
        color: #FFFFFF;
    }
    
    /* Request Card Móvil */
    .approval-card {
        background-color: #1A1D24;
        border: 1px solid #2A2F3D;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }
    .approval-card:hover {
        border-color: #F58220;
        box-shadow: 0 4px 12px rgba(245, 130, 32, 0.15);
    }
    
    .worker-name {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 2px;
    }
    .worker-role {
        font-size: 13px;
        color: #9A9EA7;
    }
    .request-date {
        font-size: 12px;
        color: #6C727F;
        float: right;
    }
    
    .metric-title {
        font-size: 12px;
        color: #9A9EA7;
        margin-top: 10px;
    }
    .metric-value-he {
        font-size: 16px;
        font-weight: 700;
        color: #F58220;
    }
    .metric-value-exceso {
        font-size: 16px;
        font-weight: 700;
        color: #E67E22;
    }
    
    /* Botones Móviles */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 44px !important;
        transition: all 0.2s !important;
    }
    
    /* Ocultar elementos pesados de escritorio en vista móvil */
    div[data-testid="stNotification"] {
        display: none !important;
    }
    
    /* Adaptar botones de pestañas móviles */
    div[data-baseweb="tab-list"] button {
        font-size: 14px !important;
        padding: 8px 12px !important;
    }

    /* Reducir espacio superior en celular */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* Badges de Estado */
    .badge-approved {
        background-color: rgba(39, 174, 96, 0.15);
        color: #27AE60;
        border: 1px solid #27AE60;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-rejected {
        background-color: rgba(231, 76, 60, 0.15);
        color: #E74C3C;
        border: 1px solid #E74C3C;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-pending {
        background-color: rgba(243, 156, 18, 0.15);
        color: #F39C12;
        border: 1px solid #F39C12;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }

    /* Bordes finos uniformes idénticos al botón popover nativo */
    div[data-testid="stForm"],
    div[data-baseweb="input"],
    .stTextInput > div > div {
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"]:focus-within, .stTextInput > div > div:focus-within {
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
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
    </style>
    """, unsafe_allow_html=True)
    
    # 2. Header Superior GZG
    st.markdown("""
    <div class="mobile-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="gzg-logo-text">GZG</span> <span class="gzg-logo-text gzg-orange">MINERALES</span>
                <div style="font-size: 11px; color: #9A9EA7; letter-spacing: 1px;">CONTROL DE ASISTENCIA Y APROBACIONES</div>
            </div>
            <div style="background: #252A34; padding: 8px 12px; border-radius: 20px; font-size: 14px;">
                🔔 <b style="color: #F58220;">3</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Usuario actual y rol
    user_info = get_current_user()
    if user_info:
        username = user_info.get('username', 'usuario')
        rol = user_info.get('rol', 'SUPERVISOR')
        nombre = user_info.get('nombre_completo', username)
    else:
        username = st.session_state.get('username', 'admin')
        rol = st.session_state.get('user_role', 'ADMINISTRACION')
        nombre = username
    
    curr_user_clean = str(username).strip().lower()
    is_admin = (rol == 'ADMINISTRACION' or curr_user_clean == 'admin')
    
    col_usr_info, col_usr_pw = st.columns([1.5, 1])
    with col_usr_info:
        st.write(f"👋 **Hola, {nombre}** ({rol})")
    with col_usr_pw:
        with st.popover("🔑 Mi Clave"):
            st.markdown("##### 🔑 Cambiar Contraseña")
            with st.form("form_cambiar_pass_mobile"):
                p_act = st.text_input("Contraseña Actual", type="password", key="m_p_act")
                p_nue = st.text_input("Nueva Contraseña", type="password", key="m_p_nue")
                p_cnf = st.text_input("Confirmar Nueva Contraseña", type="password", key="m_p_cnf")
                btn_ch = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
                if btn_ch:
                    if user_info and not verify_password(p_act, user_info.get('password_hash', '')):
                        st.error("La contraseña actual es incorrecta.")
                    elif not p_nue or len(p_nue) < 4:
                        st.warning("Debe tener al menos 4 caracteres.")
                    elif p_nue != p_cnf:
                        st.error("Las contraseñas no coinciden.")
                    else:
                        new_h = hash_password(p_nue)
                        if cambiar_password_usuario(username, new_h):
                            st.toast("🎉 ¡Contraseña actualizada!", icon="🔑")
                            st.success("Contraseña modificada exitosamente.")
                            st.rerun()
                        else:
                            st.error("Error al actualizar la contraseña.")
    
    # Sincronizar data de aprobaciones desde asistencia SQLite
    sincronizar_aprobaciones_desde_asistencia()
    df_all = obtener_solicitudes_aprobacion('TODAS')
    
    # 4. Navegación Móvil de 3 Pestañas
    tab_pendientes, tab_historial, tab_dashboard = st.tabs([
        "📋 Pendientes", "📜 Historial", "📊 Dashboard"
    ])
    
    # ---------------------------------------------------------
    # TAB 1: PENDIENTES DE APROBACIÓN POR NIVEL 1 Y NIVEL 2
    # ---------------------------------------------------------
    with tab_pendientes:
        df_base_pend = df_all[df_all['estado'] == 'PENDIENTE'].copy()
        
        # Filtrar solicitudes según aprobador N1 o N2 asignado
        if is_admin:
            df_pendientes = df_base_pend
        else:
            def _filter_user_approvals(row):
                n1 = str(row.get('aprobador_n1', '') or '').strip().lower()
                n2 = str(row.get('aprobador_n2', '') or '').strip().lower()
                st1 = str(row.get('estado_n1', 'PENDIENTE') or 'PENDIENTE').upper()
                st2 = str(row.get('estado_n2', 'PENDIENTE') or 'PENDIENTE').upper()

                # Caso 1: Usuario es Aprobador Nivel 1 y N1 está PENDIENTE
                if n1 == curr_user_clean and st1 == 'PENDIENTE':
                    return True
                # Caso 2: Usuario es Aprobador Nivel 2, N1 ya está APROBADO (o sin N1) y N2 está PENDIENTE
                if n2 == curr_user_clean and st2 == 'PENDIENTE' and (st1 == 'APROBADO' or not n1 or n1 == curr_user_clean):
                    return True
                return False

            mask = df_base_pend.apply(_filter_user_approvals, axis=1)
            df_pendientes = df_base_pend[mask] if not df_base_pend.empty else pd.DataFrame()

        df_aprobadas_mes = df_all[df_all['estado'] == 'APROBADO']
        
        # KPIs superiores
        col_kpi1, col_kpi2 = st.columns(2)
        with col_kpi1:
            st.markdown(f"""
            <div class="kpi-card-pending">
                <div style="font-size: 26px; font-weight: 800;">{len(df_pendientes)}</div>
                <div style="font-size: 12px; opacity: 0.9;">Pendientes para ti</div>
            </div>
            """, unsafe_allow_html=True)
        with col_kpi2:
            st.markdown(f"""
            <div class="kpi-card-alert">
                <div style="font-size: 26px; font-weight: 800; color: #F58220;">{len(df_aprobadas_mes)}</div>
                <div style="font-size: 12px; color: #9A9EA7;">Aprobadas este mes</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Solicitudes Asignadas para tu Aprobación")
        
        if df_pendientes.empty:
            st.info("🎉 ¡Excelente! No tienes solicitudes pendientes de aprobación en este momento.")
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
                
                n1_user = str(row.get('aprobador_n1', '') or '').strip().lower()
                n2_user = str(row.get('aprobador_n2', '') or '').strip().lower()
                st1_val = str(row.get('estado_n1', 'PENDIENTE') or 'PENDIENTE').upper()
                
                # Determinar si el usuario actual actúa como Nivel 1 o Nivel 2
                if is_admin:
                    target_level = 1 if st1_val == 'PENDIENTE' else 2
                elif n1_user == curr_user_clean and st1_val == 'PENDIENTE':
                    target_level = 1
                else:
                    target_level = 2

                level_badge = "🥇 APROBACIÓN NIVEL 1 (SUPERVISOR / JEFE)" if target_level == 1 else "🥈 APROBACIÓN NIVEL 2 (SUPERINTENDENTE)"

                avatar_url = get_worker_avatar_url(row.get('dni'), worker_name)

                with st.expander(f"👤 **{worker_name}** | {cargo} ({fecha_sol})", expanded=True):
                    st.caption(f"🛡️ **{level_badge}**")
                    if target_level == 2 and st1_val == 'APROBADO':
                        ap_por_1 = row.get('aprobado_por_n1', n1_user)
                        st.success(f"✅ Nivel 1 ya fue APROBADO por `{ap_por_1}`. Falta VoBo Final del Superintendente.")

                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 12px; margin: 8px 0 14px 0;">
                        <img src="{avatar_url}" style="width: 44px; height: 44px; border-radius: 50%; border: 2px solid #F58220; object-fit: cover; flex-shrink: 0;" />
                        <div>
                            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">{worker_name}</div>
                            <div style="font-size: 12px; color: #9A9EA7;">{cargo} ({fecha_sol})</div>
                        </div>
                    </div>

                    **Detalle de la Solicitud:**
                    - 📅 **Fecha**: {fecha_sol}
                    - 🕒 **Entrada**: `{row.get('entrada', '-')}` | **Salida**: `{row.get('salida', '-')}`
                    - ⏱️ **Jornada trabajada**: {row.get('jornada_trabajada_hhmm', '-')}
                    - ⏰ **Horas extras**: <b style="color: #F58220;">{he_hhmm}</b>
                    - ⚠️ **Exceso de jornada**: <b style="color: #E67E22;">{exceso_hhmm}</b>
                    """, unsafe_allow_html=True)
                    
                    comentario_aprobador = st.text_input(
                        "✍️ Comentario del Aprobador",
                        key=f"com_{sol_id}",
                        placeholder=""
                    )
                    
                    uploaded_file = st.file_uploader(
                        "📷 Adjuntar Foto / Imagen de Sustento (opcional)",
                        type=["png", "jpg", "jpeg"],
                        key=f"file_{sol_id}"
                    )
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button(f"❌ RECHAZAR (N{target_level})", key=f"rej_{sol_id}", use_container_width=True):
                            adjunto_rel_path = None
                            if uploaded_file is not None:
                                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                                adj_dir = os.path.join(root_dir, "downloads", "adjuntos_aprobaciones")
                                os.makedirs(adj_dir, exist_ok=True)
                                fname = f"solic_{sol_id}_{uploaded_file.name}"
                                fpath = os.path.join(adj_dir, fname)
                                with open(fpath, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                adjunto_rel_path = os.path.join("downloads", "adjuntos_aprobaciones", fname)

                            actualizar_estado_aprobacion_nivel(sol_id, target_level, 'RECHAZADO', username, comentario_aprobador, adjunto_rel_path)
                            st.success(f"Solicitud Nivel {target_level} de {worker_name} RECHAZADA.")
                            st.rerun()
                    with c_btn2:
                        btn_label = "✅ APROBAR N1" if target_level == 1 else "⭐ VoBo FINAL N2"
                        if st.button(btn_label, key=f"app_{sol_id}", type="primary", use_container_width=True):
                            adjunto_rel_path = None
                            if uploaded_file is not None:
                                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                                adj_dir = os.path.join(root_dir, "downloads", "adjuntos_aprobaciones")
                                os.makedirs(adj_dir, exist_ok=True)
                                fname = f"solic_{sol_id}_{uploaded_file.name}"
                                fpath = os.path.join(adj_dir, fname)
                                with open(fpath, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                adjunto_rel_path = os.path.join("downloads", "adjuntos_aprobaciones", fname)

                            actualizar_estado_aprobacion_nivel(sol_id, target_level, 'APROBADO', username, comentario_aprobador, adjunto_rel_path)
                            st.toast(f"✅ Solicitud de {worker_name} Aprobada en Nivel {target_level}!", icon="🎉")
                            st.success(f"Solicitud Nivel {target_level} de {worker_name} APROBADA.")
                            st.rerun()

    # ---------------------------------------------------------
    # TAB 2: HISTORIAL DE APROBACIONES
    # ---------------------------------------------------------
    with tab_historial:
        st.subheader("Historial de Aprobaciones")
        
        filtro_estado = st.radio("Filtrar por estado:", ["TODAS", "APROBADAS", "RECHAZADAS"], horizontal=True)
        
        df_hist = df_all.copy()
        if filtro_estado == "APROBADAS":
            df_hist = df_hist[df_hist['estado'] == 'APROBADO']
        elif filtro_estado == "RECHAZADAS":
            df_hist = df_hist[df_hist['estado'] == 'RECHAZADO']
            
        if df_hist.empty:
            st.info("No hay registros en el historial para el filtro seleccionado.")
        else:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            for idx, row in df_hist.iterrows():
                worker_name = f"{row.get('nombres', '')} {row.get('apellidos', '')}".title()
                cargo = row.get('cargo', '')
                fecha_sol = row.get('fecha', '')
                estado = row.get('estado', 'PENDIENTE')
                he_hhmm = row.get('horas_extras_hhmm', '0h 00m')
                exceso_hhmm = row.get('exceso_jornada_hhmm', '0h 00m')
                
                ap_n1 = row.get('aprobado_por_n1', '')
                c_n1 = row.get('comentario_n1', '')
                ap_n2 = row.get('aprobado_por_n2', '')
                c_n2 = row.get('comentario_n2', '')
                adjunto = row.get('adjuntos', '')
                
                badge_html = f'<span class="badge-approved">APROBADO</span>' if estado == 'APROBADO' else (
                    f'<span class="badge-rejected">RECHAZADO</span>' if estado == 'RECHAZADO' else f'<span class="badge-pending">PENDIENTE</span>'
                )
                
                st.markdown(f"""
                <div class="approval-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div class="worker-name">{worker_name}</div>
                            <div class="worker-role">{cargo} ({fecha_sol})</div>
                        </div>
                        <div>{badge_html}</div>
                    </div>
                    <hr style="border-color: #2A2F3D; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 13px;">
                        <div>⏰ Horas extras: <b style="color: #F58220;">{he_hhmm}</b></div>
                        <div>⚠️ Exceso: <b style="color: #E67E22;">{exceso_hhmm}</b></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if ap_n1 or c_n1:
                    st.markdown(f"💬 **Aprobador N1 ({ap_n1 or 'Supervisor'})**: {c_n1 or 'Sin comentario'}")
                if ap_n2 or c_n2:
                    st.markdown(f"⭐ **Aprobador N2 ({ap_n2 or 'Superintendente'})**: {c_n2 or 'Sin comentario'}")
                if adjunto and isinstance(adjunto, str) and adjunto.strip():
                    full_adj_path = os.path.join(root_dir, adjunto)
                    if os.path.exists(full_adj_path):
                        ext = os.path.splitext(full_adj_path)[1].lower()
                        if ext in ['.png', '.jpg', '.jpeg']:
                            st.image(full_adj_path, caption="📎 Sustento Adjuntado", use_container_width=True)
                        else:
                            st.download_button(
                                label="📎 Descargar Sustento Adjuntado",
                                data=open(full_adj_path, "rb").read(),
                                file_name=os.path.basename(full_adj_path),
                                mime="application/pdf",
                                key=f"dl_{row['id']}"
                            )
                st.divider()

    # ---------------------------------------------------------
    # TAB 3: DASHBOARD Y ESTADÍSTICAS
    # ---------------------------------------------------------
    with tab_dashboard:
        st.subheader("Dashboard de Aprobaciones")
        
        n_aprob = len(df_all[df_all['estado'] == 'APROBADO'])
        n_rech = len(df_all[df_all['estado'] == 'RECHAZADO'])
        n_pend = len(df_all[df_all['estado'] == 'PENDIENTE'])
        total_sol = len(df_all)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Horas Extras Aprobadas", f"{n_aprob}")
        c2.metric("Excesos Aprobados", f"{n_aprob}")
        c3.metric("Pendientes", f"{n_pend}")
        
        if total_sol > 0:
            pct_aprob = round((n_aprob / total_sol) * 100, 1)
            pct_rech = round((n_rech / total_sol) * 100, 1)
            pct_pend = round((n_pend / total_sol) * 100, 1)
            
            chart_df = pd.DataFrame({
                'Estado': ['Aprobadas', 'Rechazadas', 'Pendientes'],
                'Cantidad': [n_aprob, n_rech, n_pend]
            })
            
            st.write("### Solicitudes por estado")
            st.bar_chart(chart_df.set_index('Estado'))
            
            st.markdown(f"""
            - 🟢 **Aprobadas**: {pct_aprob}% ({n_aprob})
            - 🔴 **Rechazadas**: {pct_rech}% ({n_rech})
            - 🟡 **Pendientes**: {pct_pend}% ({n_pend})
            """)
