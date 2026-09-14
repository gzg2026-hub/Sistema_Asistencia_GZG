import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="GZG Minerales - Sistema Migrado", page_icon="⚖️", layout="centered")

components.html("""
<script>
    try {
        window.top.location.replace("https://chronic-acid-ooo-divide.trycloudflare.com/");
    } catch(e) {
        window.location.replace("https://chronic-acid-ooo-divide.trycloudflare.com/");
    }
</script>
""", height=0)

st.markdown("""
<div style="background:#1A1D24; border:2px solid #ef4444; border-radius:16px; padding:28px 20px; text-align:center; color:#FFFFFF; font-family:sans-serif; margin-top:20px;">
    <div style="font-size:44px; margin-bottom:12px;">⚠️</div>
    <h2 style="color:#ef4444; margin:0 0 12px 0; font-size:20px; font-weight:800;">APLICACIÓN ANTERIOR DESACTIVADA</h2>
    <p style="color:#94a3b8; font-size:14px; line-height:1.6; margin-bottom:24px;">
        Esta versión en Streamlit ha sido <b>desactivada y dada de baja</b> para evitar confusiones y garantizar la seguridad de las aprobaciones.<br><br>
        Todo el sistema opera ahora de forma unificada (Asistencia + Control de Balanza) en la nueva plataforma de alta velocidad.
    </p>
    <a href="https://chronic-acid-ooo-divide.trycloudflare.com/" target="_top" style="display:block; background:linear-gradient(135deg, #F58220 0%, #D35400 100%); color:#FFFFFF; font-weight:800; text-decoration:none; padding:15px; border-radius:12px; font-size:15px; box-shadow:0 4px 15px rgba(245,130,32,0.4);">
        🚀 Abrir Nueva Plataforma GZG
    </a>
</div>
""", unsafe_allow_html=True)
st.stop()
