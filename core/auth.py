import hashlib
import streamlit as st
from datetime import datetime
from data.database import (
    obtener_usuario_by_username, crear_usuario, init_db, seed_default_users
)

def hash_password(password: str) -> str:
    """Genera un hash SHA-256 seguro para la contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado."""
    return hash_password(password) == password_hash

def init_auth():
    """Inicializa la tabla de usuarios y asegura usuarios por defecto."""
    init_db()
    seed_default_users(hash_password)

def login_user(username: str, password: str) -> bool:
    """Intenta iniciar sesión para el usuario ingresado."""
    if not username or not password:
        return False
    init_auth()
    user = obtener_usuario_by_username(username.strip())
    if user and user.get('activo', 1) == 1:
        if verify_password(password.strip(), user['password_hash']):
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
    """Cierra la sesión del usuario actual."""
    st.session_state['authenticated'] = False
    st.session_state['user'] = None

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
