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

# ── Carpetas de descargas y procesamiento ──────────────────────────────────────
CARPETA_DATA_CRUDA = os.path.join(ROOT_DIR, "downloads", "data_cruda")
CARPETA_DATA_PROCESADA = os.path.join(ROOT_DIR, "downloads", "data_procesada")
CARPETA_DOWNLOADCENTER = r"C:\Users\GZG Minerales 2026\HCWebControlService\Downloadcenter"

os.makedirs(CARPETA_DATA_CRUDA, exist_ok=True)
os.makedirs(CARPETA_DATA_PROCESADA, exist_ok=True)

LOG_FILE = os.path.join(ROOT_DIR, "logs", "descarga_diaria.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def _log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{ts}] {msg}"
    try:
        print(linea)
    except Exception:
        print(linea.encode('ascii', errors='replace').decode('ascii'))
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def _sincronizar_downloadcenter():
    """Copia archivos de data cruda exportados manualmente en Downloadcenter hacia downloads/data_cruda."""
    if os.path.exists(CARPETA_DOWNLOADCENTER):
        try:
            import shutil
            for root_dir, dirs, files in os.walk(CARPETA_DOWNLOADCENTER):
                for f in files:
                    if f.endswith(".xlsx") and not f.startswith("~$"):
                        src = os.path.join(root_dir, f)
                        dst = os.path.join(CARPETA_DATA_CRUDA, f)
                        if not os.path.exists(dst):
                            shutil.copy2(src, dst)
                            _log(f"Sincronizado archivo desde Downloadcenter: {f}")
        except Exception as e:
            _log(f"Aviso al sincronizar Downloadcenter: {e}")


def _ejecutar_descarga(fecha_inicio: str, fecha_fin: str):
    """Descarga, procesa y guarda las transacciones del rango de fechas dado."""
    _log("=" * 60)
    _log(f"Descargando transacciones del {fecha_inicio} al {fecha_fin}...")

    # Sincronizar descargas manuales de Downloadcenter si existen
    _sincronizar_downloadcenter()

    try:
        from core.hikvision_downloader import descargar_transacciones_hikvision
        from data.data_loader import cargar_datos_excel, fusionar_y_deduplicar_data_cruda
        from core.attendance_engine import procesar_asistencia_df
        from data.database import (guardar_trabajadores, guardar_marcaciones_raw,
                                   guardar_asistencia_y_reportes)
        from data.exporter import guardar_excel_base, exportar_asistencia_excel
        from scripts.gdrive_uploader import subir_archivo_a_gdrive

        # 1. Descargar Data Cruda 1:1 desde Hikvision en downloads/data_cruda/
        excel_path_nuevo = descargar_transacciones_hikvision(
            carpeta_destino=CARPETA_DATA_CRUDA,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        _log(f"Data Cruda descargada en: {excel_path_nuevo}")

        # 2. Cargar y Fusionar en el Archivo Maestro de Data Cruda sin Duplicados ni Faltantes
        df_trab_nuevo, df_marc_nuevo, df_he_nuevo = cargar_datos_excel(excel_path_nuevo)
        
        ruta_maestro_raw = os.path.join(CARPETA_DATA_CRUDA, "Transacciones_Acumuladas.xlsx")
        df_marc_master = fusionar_y_deduplicar_data_cruda(df_marc_nuevo, ruta_maestro_raw)

        # Fallback a base de datos de trabajadores si el Excel crudo no incluye pestaña de trabajadores
        df_trab = df_trab_nuevo
        if df_trab.empty:
            from data.database import obtener_trabajadores_master
            df_trab = obtener_trabajadores_master()

        _log(f"Data Cruda Maestro Acumulada: {len(df_marc_master)} marcaciones limpias sin duplicados, {len(df_trab)} trabajadores")

        if not df_marc_master.empty:
            # Guardar el Archivo Maestro de Data Cruda en Excel
            try:
                import openpyxl
                wb_m = openpyxl.Workbook()
                ws_m = wb_m.active
                ws_m.title = "Transacciones"
                cols_m = df_marc_master.columns.tolist()
                ws_m.append(cols_m)
                for r_m in df_marc_master.itertuples(index=False):
                    ws_m.append(list(r_m))
                wb_m.save(ruta_maestro_raw)
                _log(f"Archivo Maestro Data Cruda guardado en: {ruta_maestro_raw}")
            except Exception as e_m:
                _log(f"Aviso guardando maestro data cruda: {e_m}")

            # Subir Data Cruda Maestro a Google Drive
            subir_archivo_a_gdrive(ruta_maestro_raw, subfolder_name="Data_Cruda")

            guardar_marcaciones_raw(df_marc_master, archivo_origen=ruta_maestro_raw)
            if not df_trab.empty:
                guardar_trabajadores(df_trab)
                df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc_master)
                guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)
                
                # 3. Guardar Reporte Consolidado Período Completo en la raíz y en data_procesada
                guardar_excel_base(df_trab, df_marc_master, df_asis, df_he_out, df_inc)
                _log(f"Procesamiento consolidado completado. Guardado en carpeta raíz y downloads/data_procesada/.")

                # 4. Generar y Subir Archivos Procesados Diarios por Fecha Cerrada (Día Anterior)
                carp_diario = os.path.join(CARPETA_DATA_PROCESADA, "diario")
                os.makedirs(carp_diario, exist_ok=True)

                hoy_str = datetime.date.today().strftime("%Y-%m-%d")
                if 'FECHA' in df_asis.columns:
                    fechas_unicas = sorted([str(f) for f in df_asis['FECHA'].dropna().unique()])
                    for f_dia in fechas_unicas:
                        # Si la fecha es anterior a hoy (día cerrado), generar y subir archivo diario
                        df_asis_dia = df_asis[df_asis['FECHA'].astype(str) == f_dia]
                        if not df_asis_dia.empty:
                            file_name_dia = f"Reporte_Asistencia_GZG_{f_dia}.xlsx"
                            file_path_dia = os.path.join(carp_diario, file_name_dia)

                            # Generar bytes de Excel
                            excel_bytes = exportar_asistencia_excel(df_trab, df_marc_master, df_asis_dia, df_he_out, df_inc)
                            with open(file_path_dia, "wb") as f_out:
                                f_out.write(excel_bytes)
                            _log(f"Reporte diario procesado generado para {f_dia} -> {file_path_dia}")

                            # Subir a Google Drive solo los días cerrados (anteriores a hoy) o el consolidado
                            if f_dia < hoy_str:
                                subir_archivo_a_gdrive(file_path_dia, subfolder_name="Data_Procesada")
            else:
                _log("AVISO: No se encontraron trabajadores en la base de datos para procesar asistencia.")
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
    """Servicio que espera hasta las 09:00 AM y ejecuta la descarga del día anterior."""
    try:
        import schedule
    except ImportError:
        os.system(f'"{sys.executable}" -m pip install schedule')
        import schedule

    _log("Servicio de descarga diaria iniciado.")
    _log(f"  Horario    : todos los días a las 09:00 AM")
    _log(f"  Descarga   : día ANTERIOR al de ejecución (ayer)")
    _log(f"  Data Cruda : {CARPETA_DATA_CRUDA}")
    _log(f"  Procesada  : {CARPETA_DATA_PROCESADA}")
    _log(f"  Log        : {LOG_FILE}")

    def _tarea_9am():
        fecha = _ayer()
        _log(f"Tarea programada: descargando día anterior = {fecha}")
        _ejecutar_descarga(fecha, fecha)

    schedule.every().day.at("09:00").do(_tarea_9am)

    while True:
        schedule.run_pending()
        time.sleep(30)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    args = sys.argv[1:]

    if not args or args[0].lower() in ("ahora", "now", "auto", "automatico"):
        # Modo por defecto / Tarea Programada de Windows (a las 9:00 AM):
        # Descarga el rango de AYER a HOY para incluir salidas matutinas de turno noche
        ini = _ayer()
        fin = _hoy()
        _log(f"Ejecución AUTOMÁTICA (9:00 AM): descargando rango {ini} -> {fin} para emparejamiento completo de Turno Noche...")
        _ejecutar_descarga(ini, fin)

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
        _log(f"Ejecución MANUAL con rango: {ini} -> {fin}")
        _ejecutar_descarga(ini, fin)

    else:
        print(__doc__)
