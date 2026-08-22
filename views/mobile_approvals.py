import streamlit as st
import pandas as pd
import datetime
from data.database import obtener_solicitudes_aprobacion, actualizar_estado_aprobacion, sincronizar_aprobaciones_desde_asistencia

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
    
    # 3. Usuario actual
    username = st.session_state.get('username', 'Supervisor')
    rol = st.session_state.get('user_role', 'SUPERVISOR')
    
    st.write(f"👋 **Hola, {username}** ({rol})")
    
    # Sincronizar data de aprobaciones desde asistencia SQLite
    sincronizar_aprobaciones_desde_asistencia()
    df_all = obtener_solicitudes_aprobacion('TODAS')
    
    # 4. Navegación Móvil de 4 Pestañas
    tab_pendientes, tab_historial, tab_dashboard = st.tabs([
        "📋 Pendientes", "📜 Historial", "📊 Dashboard"
    ])
    
    # ---------------------------------------------------------
    # TAB 1: PENDIENTES DE APROBACIÓN
    # ---------------------------------------------------------
    with tab_pendientes:
        df_pendientes = df_all[df_all['estado'] == 'PENDIENTE']
        df_aprobadas_mes = df_all[df_all['estado'] == 'APROBADO']
        
        # KPIs superiores
        col_kpi1, col_kpi2 = st.columns(2)
        with col_kpi1:
            st.markdown(f"""
            <div class="kpi-card-pending">
                <div style="font-size: 26px; font-weight: 800;">{len(df_pendientes)}</div>
                <div style="font-size: 12px; opacity: 0.9;">Pendientes de aprobación</div>
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
        st.subheader("Pendientes de aprobación")
        
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
                
                with st.expander(f"👤 **{worker_name}** | {cargo} ({fecha_sol})", expanded=True):
                    st.markdown(f"""
                    **Detalle de la Solicitud:**
                    - 📅 **Fecha**: {fecha_sol}
                    - 🕒 **Entrada**: `{row.get('entrada', '-')}` | **Salida**: `{row.get('salida', '-')}`
                    - ⏱️ **Jornada trabajada**: {row.get('jornada_trabajada_hhmm', '-')}
                    - ⏰ **Horas extras**: <b style="color: #F58220;">{he_hhmm}</b>
                    - ⚠️ **Exceso de jornada**: <b style="color: #E67E22;">{exceso_hhmm}</b>
                    - 📝 **Motivo**: {motivo}
                    """, unsafe_allow_html=True)
                    
                    if obs_trabajador:
                        st.info(f"💬 **Observación**: {obs_trabajador}")
                        
                    comentario = st.text_input(f"Comentario opcional ({worker_name})", key=f"com_{sol_id}", placeholder="Escribe un comentario...")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("❌ RECHAZAR", key=f"rej_{sol_id}", use_container_width=True):
                            actualizar_estado_aprobacion(sol_id, 'RECHAZADO', username, comentario)
                            st.success(f"Solicitud de {worker_name} RECHAZADA.")
                            st.rerun()
                    with c_btn2:
                        if st.button("✅ APROBAR", key=f"app_{sol_id}", type="primary", use_container_width=True):
                            actualizar_estado_aprobacion(sol_id, 'APROBADO', username, comentario)
                            st.success(f"Solicitud de {worker_name} APROBADA.")
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
            for idx, row in df_hist.iterrows():
                worker_name = f"{row.get('nombres', '')} {row.get('apellidos', '')}".title()
                cargo = row.get('cargo', '')
                fecha_sol = row.get('fecha', '')
                estado = row.get('estado', 'PENDIENTE')
                he_hhmm = row.get('horas_extras_hhmm', '0h 00m')
                exceso_hhmm = row.get('exceso_jornada_hhmm', '0h 00m')
                aprobador = row.get('aprobado_por', 'Sistema')
                f_aprob = row.get('fecha_aprobacion', '')
                
                badge_html = f'<span class="badge-approved">APROBADO</span>' if estado == 'APROBADO' else (
                    f'<span class="badge-rejected">RECHAZADO</span>' if estado == 'RECHAZADO' else f'<span class="badge-pending">PENDIENTE</span>'
                )
                
                st.markdown(f"""
                <div class="approval-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div class="worker-name">{worker_name}</div>
                            <div class="worker-role">{cargo}</div>
                        </div>
                        <div>{badge_html}</div>
                    </div>
                    <hr style="border-color: #2A2F3D; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 13px;">
                        <div>⏰ Horas extras: <b style="color: #F58220;">{he_hhmm}</b></div>
                        <div>⚠️ Exceso: <b style="color: #E67E22;">{exceso_hhmm}</b></div>
                    </div>
                    <div style="font-size: 11px; color: #6C727F; margin-top: 8px;">
                        Por: {aprobador} {f'| {f_aprob}' if f_aprob else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

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
