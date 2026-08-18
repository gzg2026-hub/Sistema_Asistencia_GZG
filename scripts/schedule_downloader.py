"""
schedule_downloader.py
======================
Descarga automática diaria de transacciones Hikvision a las 8:00 AM.
Descarga el DIA ANTERIOR al actual (ejemplo: si hoy es 18/08, descarga el 17/08).

MODOS DE USO:
  - Automático (Tarea Programada Windows): ejecutar sin argumentos
        python schedule_downloader.py

  - Manual inmediato (día anterior):
        python schedule_downloader.py ahora

  - Manual con fecha específica:
        python schedule_downloader.py manual

  - Manual con fecha desde argumento:
        python schedule_downloader.py 2026-08-17
        python schedule_downloader.py 2026-08-15 2026-08-17   (rango)
"""

import os
import sys
import time
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# ── Carpeta de descargas ──────────────────────────────────────────────────────
CARPETA_DESCARGAS = os.path.join(ROOT_DIR, "downloads", "hikvision")
os.makedirs(CARPETA_DESCARGAS, exist_ok=True)

LOG_FILE = os.path.join(ROOT_DIR, "logs", "descarga_diaria.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def _log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{ts}] {msg}"
    print(linea)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def _ejecutar_descarga(fecha_inicio: str, fecha_fin: str):
    """Descarga, procesa y guarda las transacciones del rango de fechas dado."""
    _log("=" * 60)
    _log(f"Descargando transacciones del {fecha_inicio} al {fecha_fin}...")

    try:
        from core.hikvision_downloader import descargar_transacciones_hikvision
        from data.data_loader import cargar_datos_excel
        from core.attendance_engine import procesar_asistencia_df
        from data.database import (guardar_trabajadores, guardar_marcaciones_raw,
                                   guardar_asistencia_y_reportes)
        from data.exporter import guardar_excel_base

        # 1. Descargar desde Hikvision
        excel_path = descargar_transacciones_hikvision(
            carpeta_destino=CARPETA_DESCARGAS,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        _log(f"Archivo guardado en: {excel_path}")

        # 2. Cargar datos del Excel
        df_trab, df_marc, df_he = cargar_datos_excel(excel_path)
        _log(f"Cargados: {len(df_marc)} marcaciones, {len(df_trab)} trabajadores")

        if not df_marc.empty:
            guardar_marcaciones_raw(df_marc, archivo_origen=excel_path)
            if not df_trab.empty:
                guardar_trabajadores(df_trab)
                df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)
                guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)
                guardar_excel_base(df_trab, df_marc, df_asis, df_he_out, df_inc)
                _log(f"Procesamiento completado. Marcaciones: {len(df_marc)}")
        else:
            _log("AVISO: No se encontraron marcaciones en el archivo.")

    except Exception as e:
        import traceback
        _log(f"ERROR: {e}")
        _log(traceback.format_exc())

    _log("Descarga finalizada.")
    _log("=" * 60)


def _hoy() -> str:
    return datetime.date.today().strftime("%Y-%m-%d")


def _ayer() -> str:
    return (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")


def _menu_manual():
    """Menú interactivo para elegir la fecha a descargar manualmente."""
    print("\n" + "=" * 58)
    print("  DESCARGA MANUAL DE TRANSACCIONES HIKVISION - GZG")
    print("=" * 58)
    print(f"  Fecha actual (HOY) : {_hoy()} ({datetime.date.today().strftime('%d/%m/%Y')})")
    print(f"  Día anterior (AYER): {_ayer()}")
    print("=" * 58)
    print("\n  Opciones:")
    print("  [1] Descargar el día de HOY (Día actual)")
    print("  [2] Descargar el día de AYER")
    print("  [3] Descargar una fecha específica")
    print("  [4] Descargar un rango de fechas")
    print("  [5] Salir")
    print()

    opcion = input("  Seleccione opción (1-5): ").strip()

    if opcion == "1":
        fecha = _hoy()
        print(f"\n  Descargando HOY: {fecha}")
        _ejecutar_descarga(fecha, fecha)

    elif opcion == "2":
        fecha = _ayer()
        print(f"\n  Descargando AYER: {fecha}")
        _ejecutar_descarga(fecha, fecha)

    elif opcion == "3":
        fecha_str = input("  Ingrese la fecha (DD/MM/YYYY, YYYY-MM-DD o YYYY/MM/DD): ").strip()
        fecha = _parsear_fecha(fecha_str)
        if fecha:
            print(f"\n  Descargando: {fecha}")
            _ejecutar_descarga(fecha, fecha)
        else:
            print("  Fecha inválida. Use formato DD/MM/YYYY o YYYY-MM-DD.")

    elif opcion == "4":
        ini_str = input("  Fecha inicio (DD/MM/YYYY, YYYY-MM-DD o YYYY/MM/DD): ").strip()
        fin_str = input("  Fecha fin    (DD/MM/YYYY, YYYY-MM-DD o YYYY/MM/DD): ").strip()
        ini = _parsear_fecha(ini_str)
        fin = _parsear_fecha(fin_str)
        if ini and fin:
            if ini > fin:
                ini, fin = fin, ini
            print(f"\n  Descargando rango: {ini} → {fin}")
            _ejecutar_descarga(ini, fin)
        else:
            print("  Fechas inválidas.")

    elif opcion == "5":
        print("  Saliendo.")
    else:
        print("  Opción inválida.")

    input("\n  Presione Enter para cerrar...")


def _parsear_fecha(s: str) -> str | None:
    """Acepta DD/MM/YYYY, YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY y devuelve YYYY-MM-DD."""
    s = str(s).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _iniciar_programador():
    """Servicio que espera hasta las 08:00 AM y ejecuta la descarga del día anterior."""
    try:
        import schedule
    except ImportError:
        os.system(f'"{sys.executable}" -m pip install schedule')
        import schedule

    _log("Servicio de descarga diaria iniciado.")
    _log(f"  Horario    : todos los días a las 08:00 AM")
    _log(f"  Descarga   : día ANTERIOR al de ejecución (ayer)")
    _log(f"  Archivos   : {CARPETA_DESCARGAS}")
    _log(f"  Log        : {LOG_FILE}")

    def _tarea_8am():
        fecha = _ayer()
        _log(f"Tarea programada: descargando día anterior = {fecha}")
        _ejecutar_descarga(fecha, fecha)

    schedule.every().day.at("08:00").do(_tarea_8am)

    while True:
        schedule.run_pending()
        time.sleep(30)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    args = sys.argv[1:]

    if not args or args[0].lower() in ("ahora", "now", "auto", "automatico"):
        # Modo por defecto / Tarea Programada de Windows:
        # Ejecutar INMEDIATAMENTE la descarga del día anterior y finalizar cleanly.
        fecha = _ayer()
        _log(f"Ejecución AUTOMÁTICA / INMEDIATA: descargando día anterior = {fecha}")
        _ejecutar_descarga(fecha, fecha)

    elif args[0].lower() in ("daemon", "service", "servicio"):
        # Modo servicio continuo 24/7 (bucle)
        _iniciar_programador()

    elif args[0].lower() == "manual":
        # Menú interactivo para elegir fecha
        _menu_manual()

    elif len(args) == 1 and _parsear_fecha(args[0]):
        # Fecha específica como argumento: python schedule_downloader.py 2026-08-17
        fecha = _parsear_fecha(args[0])
        _log(f"Ejecución MANUAL con fecha: {fecha}")
        _ejecutar_descarga(fecha, fecha)

    elif len(args) == 2 and _parsear_fecha(args[0]) and _parsear_fecha(args[1]):
        # Rango: python schedule_downloader.py 2026-08-15 2026-08-17
        ini = _parsear_fecha(args[0])
        fin = _parsear_fecha(args[1])
        _log(f"Ejecución MANUAL con rango: {ini} → {fin}")
        _ejecutar_descarga(ini, fin)

    else:
        print(__doc__)
