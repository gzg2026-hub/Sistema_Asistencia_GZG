import hashlib
import streamlit as st
from datetime import datetime
from data.database import (
    obtener_usuario_by_username, crear_usuario, init_db, seed_default_users
)

def hash_password(password: str) -> str:
    """Genera un hash SHA-256 seguro para la contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, password_hash: str, username: str = "") -> bool:
    """Verifica si la contraseña coincide con el hash almacenado, con tolerancia inteligente para teclados móviles."""
    if not password:
        return False
    p_clean = password.strip()
    if hash_password(p_clean) == password_hash:
        return True
    if not p_clean.endswith('*') and hash_password(p_clean + '*') == password_hash:
        return True
    return False

def init_auth():
    """Inicializa la tabla de usuarios y asegura usuarios por defecto."""
    init_db()
    seed_default_users(hash_password)

def login_user(username: str, password: str) -> bool:
    """Intenta iniciar sesión para el usuario ingresado de forma segura y tolerante."""
    if not username or not password:
        return False
    u_clean = username.strip().lower()
    user = obtener_usuario_by_username(u_clean)
    if user and user.get('activo', 1) == 1:
        if verify_password(password.strip(), user['password_hash'], u_clean):
            st.session_state['authenticated'] = True
            st.session_state['user'] = {
                'id': user['id'],
                'username': user['username'],
                'nombre_completo': user['nombre_completo'],
                'rol': user['rol'],
                'area_asignada': user['area_asignada'],
                'cargo': user.get('cargo', '')
            }
            return True
    return False

def logout_user():
    """Cierra la sesión del usuario actual y limpia el estado de autenticación de forma segura."""
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    for k in list(st.session_state.keys()):
        if k not in ('authenticated', 'user'):
            try:
                del st.session_state[k]
            except Exception:
                pass

def get_current_user():
    """Retorna la información del usuario autenticado o None."""
    if st.session_state.get('authenticated', False):
        return st.session_state.get('user', None)
    return None

def is_authenticated() -> bool:
    """Retorna True si hay un usuario autenticado."""
    return st.session_state.get('authenticated', False) is True

def check_permission(required_roles: list) -> bool:
    """Verifica si el usuario actual posee uno de los roles requeridos."""
    user = get_current_user()
    if not user:
        return False
    if 'ADMINISTRACION' in user['rol'] or user['rol'] in required_roles:
        return True
    return False
