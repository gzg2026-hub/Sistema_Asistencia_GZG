"""
push_notifications.py
======================
Módulo oficial de Notificaciones Web Push para PWA Móvil de GZG Minerales.
Permite enviar alertas nativas push a los celulares de los supervisores
(Jhon Alva, Jhon Ágreda, Josmell Huayama, Manuel Sánchez, etc.) cuando tienen
solicitudes de horas extras pendientes por validar.
"""

import os
import sys
import json
import sqlite3
import datetime
from pywebpush import webpush, WebPushException

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from data.database import DB_PATH, get_connection

# Claves VAPID Estándar para GZG Minerales PWA
VAPID_PUBLIC_KEY = (
    "BNYv9m_L7eBfS8W5kG0nL_j8bYc9Kx_mQxP7zR8tY6wV3bA1cE5nK9dL3mQ7zR5tY8wV1bA3cE5nK7dL9mQ1zR=="
)
# Ruta del archivo de claves privadas VAPID
VAPID_KEY_FILE = os.path.join(ROOT_DIR, "data", "vapid_keys.json")
VAPID_CLAIMS_EMAIL = "mailto:soporte@gzgminerales.com"


def inicializar_tabla_push(db_path: str = DB_PATH):
    """Crea la tabla de suscripciones push en SQLite si no existe."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            endpoint TEXT UNIQUE NOT NULL,
            p256dh TEXT NOT NULL,
            auth TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_push_user ON push_subscriptions (username)")
    conn.commit()
    conn.close()


def obtener_o_crear_claves_vapid() -> dict:
    """Obtiene o genera el par de claves VAPID criptográficas para Web Push."""
    if os.path.exists(VAPID_KEY_FILE):
        try:
            with open(VAPID_KEY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass

    from py_vapid import Vapid, utils
    from cryptography.hazmat.primitives import serialization
    v = Vapid()
    v.generate_keys()
    raw_pub = v.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    b64_pub = utils.b64urlencode(raw_pub)
    
    keys = {
        "public_key_b64": b64_pub,
        "private_key": v.private_pem().decode("utf-8")
    }
    os.makedirs(os.path.dirname(VAPID_KEY_FILE), exist_ok=True)
    with open(VAPID_KEY_FILE, "w") as f:
        json.dump(keys, f, indent=2)
    return keys


def guardar_suscripcion_push(username: str, sub_dict: dict, db_path: str = DB_PATH) -> bool:
    """Guarda o actualiza la suscripción push del celular del supervisor en SQLite."""
    try:
        inicializar_tabla_push(db_path)
        endpoint = sub_dict.get("endpoint", "")
        keys = sub_dict.get("keys", {})
        p256dh = keys.get("p256dh", "")
        auth = keys.get("auth", "")

        if not endpoint or not p256dh or not auth:
            return False

        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO push_subscriptions (username, endpoint, p256dh, auth, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(endpoint) DO UPDATE SET
                username = excluded.username,
                p256dh = excluded.p256dh,
                auth = excluded.auth,
                updated_at = CURRENT_TIMESTAMP
        """, (username.strip().lower(), endpoint, p256dh, auth))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[WebPush] Error guardando suscripción: {e}")
        return False


def enviar_notificacion_push(
    username: str,
    titulo: str = "GZG Minerales - Asistencia",
    mensaje: str = "Tienes solicitudes de horas extras pendientes por aprobar.",
    url: str = "/",
    db_path: str = DB_PATH
) -> int:
    """
    Envía una notificación Web Push en tiempo real al teléfono del supervisor especificado.
    Retorna el número de dispositivos que recibieron la notificación con éxito.
    """
    inicializar_tabla_push(db_path)
    keys_vapid = obtener_o_crear_claves_vapid()
    
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, endpoint, p256dh, auth FROM push_subscriptions WHERE username = ?", (username.strip().lower(),))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    payload = json.dumps({
        "title": titulo,
        "body": mensaje,
        "icon": "/static/icon-192.png",
        "badge": "/static/icon-192.png",
        "url": url,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })

    enviados = 0
    ids_a_borrar = []

    for r in rows:
        sub_id, ep, p256, auth_token = r
        sub_info = {
            "endpoint": ep,
            "keys": {
                "p256dh": p256,
                "auth": auth_token
            }
        }
        try:
            webpush(
                subscription_info=sub_info,
                data=payload,
                vapid_private_key=keys_vapid["private_key"],
                vapid_claims={"sub": VAPID_CLAIMS_EMAIL}
            )
            enviados += 1
        except WebPushException as ex:
            # Si el endpoint expiró o el usuario revocó permisos (404 / 410 Gone)
            if "410" in str(ex) or "404" in str(ex):
                ids_a_borrar.append(sub_id)
            print(f"[WebPush] Aviso enviando a {username}: {ex}")
        except Exception as e:
            print(f"[WebPush] Error enviando a {username}: {e}")

    # Limpiar suscripciones caducadas
    if ids_a_borrar:
        conn = get_connection(db_path)
        conn.cursor().executemany("DELETE FROM push_subscriptions WHERE id = ?", [(i,) for i in ids_a_borrar])
        conn.commit()
        conn.close()

    return enviados


def notificar_pendientes_a_supervisores(db_path: str = DB_PATH):
    """
    Escanea la base de datos y envía notificaciones push a todos los supervisores
    que tengan solicitudes pendientes de aprobación en su bandeja personal.
    """
    try:
        from data.database import obtener_solicitudes_aprobacion
        df_all = obtener_solicitudes_aprobacion('TODAS', db_path=db_path)
        if df_all.empty:
            return

        # Nivel 1 pendientes
        df_n1 = df_all[df_all['estado_n1'] == 'PENDIENTE']
        conteo_n1 = df_n1['aprobador_n1'].value_counts()

        for supervisor, count in conteo_n1.items():
            if supervisor and str(supervisor).strip().lower() not in ('nan', 'none', '-', ''):
                enviar_notificacion_push(
                    username=str(supervisor),
                    titulo="📋 Solicitudes Pendientes (Nivel 1)",
                    mensaje=f"Tienes {count} solicitudes de Horas Extras y Excesos de Jornada pendientes por aprobar.",
                    url="/",
                    db_path=db_path
                )

        # Nivel 2 pendientes (msanchez)
        df_n2 = df_all[(df_all['estado_n2'] == 'PENDIENTE') & (df_all['estado_n1'] == 'APROBADO')]
        conteo_n2 = df_n2['aprobador_n2'].value_counts()

        for superint, count in conteo_n2.items():
            if superint and str(superint).strip().lower() not in ('nan', 'none', '-', ''):
                enviar_notificacion_push(
                    username=str(superint),
                    titulo="⭐ Aprobación Final Requerida (Nivel 2)",
                    mensaje=f"Tienes {count} solicitudes con V°B° de Guardia listas para tu aprobación final.",
                    url="/",
                    db_path=db_path
                )
    except Exception as e:
        print(f"[WebPush] Error en notificar_pendientes_a_supervisores: {e}")
