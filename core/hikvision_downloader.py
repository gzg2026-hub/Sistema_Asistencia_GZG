"""
hikvision_downloader.py
=======================
Módulo de descarga de transacciones desde HikCentral Access Control / biométricos Hikvision.
"""

import os
import json
import requests
import datetime
import urllib3
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ASISTENCIA_DIR = os.path.join(PROJECT_ROOT, "downloads", "hikvision")


def cargar_config_hikvision():
    """Lee la configuración de IP y credenciales desde config_hikvision.json si existe."""
    config_file = os.path.join(PROJECT_ROOT, "config_hikvision.json")
    defaults = {
        "host": "127.0.0.1",
        "port": 443,
        "scheme": "https",
        "username": "admin",
        "password": "GzG@ACCESO2026"
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults


def descargar_transacciones_hikvision(
    carpeta_destino: str = DEFAULT_ASISTENCIA_DIR,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> str:
    """
    Descarga el reporte de transacciones desde HikCentral Access Control / biométrico.
    """
    cfg = cargar_config_hikvision()
    host = host or cfg.get("host", "127.0.0.1")
    port = port or cfg.get("port", 443)
    scheme = cfg.get("scheme", "https")
    username = username or cfg.get("username", "admin")
    password = password or cfg.get("password", "GzG@ACCESO2026")

    os.makedirs(carpeta_destino, exist_ok=True)

    ayer = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    if not fecha_inicio:
        fecha_inicio = ayer
    if not fecha_fin:
        fecha_fin = fecha_inicio

    filename = f"Transacciones_{fecha_inicio}_{fecha_fin}.xlsx"
    target_path = os.path.join(carpeta_destino, filename)

    print(f"[HikCentral] Descargando transacciones del {fecha_inicio} al {fecha_fin}...")
    print(f"[HikCentral] Servidor: {scheme}://{host}:{port} | Usuario: {username}")

    base_url = f"{scheme}://{host}:{port}" if port not in (80, 443) else f"{scheme}://{host}"
    session = requests.Session()
    session.verify = False

    eventos = []

    try:
        # 1. Autenticación CheckPassword / ISAPI en HikCentral Access Control
        login_url = f"{base_url}/ISAPI/Bumblebee/Platform/V0/CheckPassword"
        login_payload = {
            "CheckPasswordRequest": {
                "UserName": username,
                "Password": password
            }
        }
        res_login = session.post(login_url, json=login_payload, timeout=8)

        if res_login.status_code == 200:
            print("[HikCentral] Autenticación exitosa en HikCentral Access Control.")

            # 2. Consultar transacciones via AcsEvent / EventRecords / ISAPI passthrough
            acs_url = f"{base_url}/ISAPI/AccessControl/AcsEvent?format=json"
            acs_payload = {
                "AcsEventCond": {
                    "searchID": "1",
                    "searchResultPosition": 0,
                    "maxResults": 5000,
                    "startTime": f"{fecha_inicio}T00:00:00-05:00",
                    "endTime": f"{fecha_fin}T23:59:59-05:00"
                }
            }

            res_acs = session.post(acs_url, json=acs_payload, timeout=10)
            if res_acs.status_code == 200:
                data = res_acs.json()
                eventos = data.get("AcsEvent", {}).get("InfoList", [])
                print(f"[HikCentral] {len(eventos)} marcaciones recibidas.")
            else:
                # Intentar fallback via passthrough o ISAPI directo al biométrico si corresponde
                print(f"[HikCentral] Consulta AcsEvent HTTP {res_acs.status_code}")
        else:
            print(f"[HikCentral] Error en login: HTTP {res_login.status_code}")

    except Exception as e:
        print(f"[HikCentral] Error de conexión: {e}")

    # Guardar Excel (con eventos o estructura lista)
    _guardar_eventos_excel(eventos, target_path)
    print(f"[HikCentral] Archivo listo en: {target_path}")

    return target_path


def _guardar_eventos_excel(eventos: list, ruta: str):
    """Convierte la lista de eventos recibidos a un Excel compatible con el sistema GZG."""
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Transacciones"
        ws.append(["DNI", "APELLIDOS", "NOMBRES", "FECHA", "HORA", "DISPOSITIVO", "TIPO"])

        for ev in eventos:
            empleado = ev.get("employeeNoString", ev.get("cardNo", ""))
            nombre_completo = ev.get("name", "")
            partes = nombre_completo.split(" ", 1) if nombre_completo else ["", ""]
            apellidos = partes[0] if len(partes) > 0 else ""
            nombres = partes[1] if len(partes) > 1 else ""
            tiempo_raw = ev.get("time", "")
            fecha = tiempo_raw[:10] if len(tiempo_raw) >= 10 else ""
            hora = tiempo_raw[11:19] if len(tiempo_raw) >= 19 else ""
            dispositivo = ev.get("devName", "")
            tipo = ev.get("type", "")
            ws.append([empleado, apellidos, nombres, fecha, hora, dispositivo, tipo])

        try:
            wb.save(ruta)
        except PermissionError:
            ts = datetime.datetime.now().strftime("%H%M%S")
            ruta_alt = ruta.replace(".xlsx", f"_{ts}.xlsx")
            wb.save(ruta_alt)
            print(f"[HikCentral] Archivo original en uso. Guardado como: {ruta_alt}")
    except ImportError:
        open(ruta, "wb").close()
