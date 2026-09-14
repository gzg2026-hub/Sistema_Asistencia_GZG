import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="GZG Minerales - Sistema Migrado", page_icon="⚖️", layout="centered")

components.html("""
<script>
    const NUEVA_URL = "https://chronic-acid-ooo-divide.trycloudflare.com/";
    const CHROME_INTENT = "intent://chronic-acid-ooo-divide.trycloudflare.com/#Intent;scheme=https;package=com.android.chrome;end";
    function abrir() {
        const isAndroid = /android/i.test(navigator.userAgent);
        if (isAndroid) {
            try { window.location.href = CHROME_INTENT; return; } catch(e) {}
        }
        try { window.open(NUEVA_URL, '_blank', 'noopener,noreferrer'); } catch(e) {
            window.top.location.href = NUEVA_URL;
        }
    }
    setTimeout(abrir, 400);
</script>
<div style="text-align:center; padding:10px;">
    <a href="https://chronic-acid-ooo-divide.trycloudflare.com/" target="_blank" rel="noopener noreferrer" style="display:inline-block; background:linear-gradient(135deg, #F58220 0%, #D35400 100%); color:#FFFFFF; font-weight:800; text-decoration:none; padding:16px 24px; border-radius:14px; font-size:16px; font-family:sans-serif; box-shadow:0 4px 15px rgba(245,130,32,0.4);" onclick="abrir();">
        🚀 Tocar aquí para entrar al Nuevo Sistema GZG
    </a>
</div>
""", height=90)

st.markdown("""
<div style="background:#1A1D24; border:2px solid #F58220; border-radius:18px; padding:28px 20px; text-align:center; color:#FFFFFF; font-family:sans-serif; margin-top:20px; box-shadow:0 10px 30px rgba(0,0,0,0.5);">
    <div style="font-size:44px; margin-bottom:12px;">⚖️</div>
    <h2 style="color:#F58220; margin:0 0 12px 0; font-size:20px; font-weight:800;">SISTEMA GZG MIGRADO Y UNIFICADO</h2>
    <p style="color:#94a3b8; font-size:14px; line-height:1.6; margin-bottom:24px;">
        Esta versión en Streamlit ha sido <b>desactivada</b> para garantizar la seguridad.<br><br>
        Todo el control (Asistencia + Balanza de Planta) opera ahora de forma integrada en el nuevo servidor unificado.
    </p>
    <a href="https://chronic-acid-ooo-divide.trycloudflare.com/" target="_blank" rel="noopener noreferrer" style="display:block; background:linear-gradient(135deg, #F58220 0%, #D35400 100%); color:#FFFFFF; font-weight:800; text-decoration:none; padding:15px; border-radius:12px; font-size:15px; box-shadow:0 4px 15px rgba(245,130,32,0.4); margin-bottom:14px;">
        🚀 Abrir Nueva Plataforma GZG
    </a>
    <div style="background:#121418; border:1px solid #334155; border-radius:10px; padding:10px; font-size:12px; color:#38BDF8; word-break:break-all; margin-bottom:14px;">
        https://chronic-acid-ooo-divide.trycloudflare.com/
    </div>
</div>
""", unsafe_allow_html=True)
st.stop()
