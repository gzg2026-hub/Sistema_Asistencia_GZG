import os
import requests
import datetime
from typing import Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ASISTENCIA_DIR = os.path.join(PROJECT_ROOT, "downloads", "hikvision")


def descargar_transacciones_hikvision(
    carpeta_destino: str = DEFAULT_ASISTENCIA_DIR,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    host: str = "192.168.1.100",
    port: int = 80,
    username: str = "admin",
    password: str = "gzg2026*"
) -> str:
    """
    Descarga el reporte de transacciones desde el biométrico Hikvision ISAPI.

    Parámetros:
        carpeta_destino: carpeta donde guardar el archivo descargado.
        fecha_inicio: fecha de inicio en formato 'YYYY-MM-DD'. Default = ayer.
        fecha_fin:    fecha de fin   en formato 'YYYY-MM-DD'. Default = ayer.
        host:         IP del biométrico Hikvision en la red local.
        port:         Puerto HTTP del biométrico.
        username:     Usuario administrador del equipo.
        password:     Contraseña del equipo.

    Retorna:
        Ruta completa del archivo guardado.

    Lógica de fechas:
        - Automático (7 AM): descarga el DÍA ANTERIOR al actual (ayer).
        - Manual con argumentos: descarga el rango indicado.
    """
    os.makedirs(carpeta_destino, exist_ok=True)

    ayer = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    if not fecha_inicio:
        fecha_inicio = ayer
    if not fecha_fin:
        fecha_fin = fecha_inicio  # mismo día por defecto

    filename = f"Transacciones_{fecha_inicio}_{fecha_fin}.xlsx"
    target_path = os.path.join(carpeta_destino, filename)

    print(f"[Hikvision] Descargando transacciones del {fecha_inicio} al {fecha_fin}...")
    print(f"[Hikvision] Destino: {target_path}")

    # Construcción del rango ISO 8601 con zona horaria Peru (UTC-5)
    url = f"http://{host}:{port}/ISAPI/AccessControl/AcsEvent?format=json"
    payload = {
        "AcsEventCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 5000,
            "startTime": f"{fecha_inicio}T00:00:00-05:00",
            "endTime": f"{fecha_fin}T23:59:59-05:00"
        }
    }

    try:
        auth = requests.auth.HTTPDigestAuth(username, password)
        res = requests.post(url, json=payload, auth=auth, timeout=8)

        if res.status_code == 200:
            data = res.json()
            eventos = data.get("AcsEvent", {}).get("InfoList", [])
            print(f"[Hikvision] {len(eventos)} eventos recibidos. Guardando Excel...")
            _guardar_eventos_excel(eventos, target_path)
            print(f"[Hikvision] Archivo guardado: {target_path}")
        else:
            print(f"[Hikvision] Respuesta inesperada: HTTP {res.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"[Hikvision] No se pudo conectar a {host}:{port}. Verifique la red local.")
    except requests.exceptions.Timeout:
        print(f"[Hikvision] Timeout al conectar con {host}:{port}.")
    except Exception as e:
        print(f"[Hikvision] Error: {e}")

    return target_path


def _guardar_eventos_excel(eventos: list, ruta: str):
    """Convierte los eventos ISAPI a un Excel compatible con el sistema GZG."""
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

        wb.save(ruta)
    except ImportError:
        # Crear archivo vacío para que el sistema no falle si openpyxl no está
        open(ruta, "wb").close()
