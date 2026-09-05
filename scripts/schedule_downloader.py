"""
schedule_downloader.py
======================
Descarga automática de transacciones Hikvision en 3 pasadas espaciadas por la mañana
(09:00, 09:30 y 10:00), para tolerar que el biométrico físico tarde en sincronizar sus
eventos offline con el servidor HikCentral. El merge/dedup es idempotente, así que cada
pasada es segura de repetir; si una pasada no trae marcaciones nuevas respecto a la
anterior, se omite el reproceso y la subida a Drive/GitHub de esa pasada.

MODOS DE USO:
  - Manual inmediato (siempre procesa completo, sin omitir nada):
        python schedule_downloader.py
        python schedule_downloader.py ahora

  - Automático con 3 Tareas Programadas de Windows separadas (recomendado en producción):
        python schedule_downloader.py pase1   (09:00 AM)
        python schedule_downloader.py pase2   (09:30 AM)
        python schedule_downloader.py pase3   (10:00 AM, dispara la alerta de antigüedad si aplica)

  - Alternativa: un solo proceso en segundo plano (usa la librería 'schedule' internamente,
    registra las 3 pasadas automáticamente):
        python schedule_downloader.py daemon

  - Manual con fecha específica:
        python schedule_downloader.py manual

  - Manual con fecha desde argumento:
        python schedule_downloader.py 2026-08-17
        python schedule_downloader.py 2026-08-15 2026-08-17   (rango)

  - Reproceso puntual desde código (usado por el botón "Reprocesar Datos" en app.py):
        from scripts.schedule_downloader import reprocesar_fecha
        reprocesar_fecha("2026-08-29")
"""

import os
import sys
import time
import datetime
import subprocess
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# Si la marcación más reciente encontrada tras la ÚLTIMA pasada programada del día
# tiene más antigüedad que esto (en minutos), se registra una alerta visible en el log:
# probable señal de que el biométrico no terminó de sincronizar con HikCentral hoy.
UMBRAL_ALERTA_ANTIGUEDAD_MIN = 120

# Regla Oficial Inviolable: inicio oficial de operaciones biométricas en mina
FECHA_INICIO_OFICIAL = "2026-08-17"


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
    """Copia archivos de data cruda exportados manualmente en Downloadcenter hacia downloads/data_cruda si son recientes."""
    if os.path.exists(CARPETA_DOWNLOADCENTER):
        try:
            import shutil
            ahora_ts = time.time()
            for root_dir, dirs, files in os.walk(CARPETA_DOWNLOADCENTER):
                for f in files:
                    if f.endswith(".xlsx") and not f.startswith("~$") and ("transacciones" in f.lower() or "informacion personal" in f.lower()):
                        src = os.path.join(root_dir, f)
                        # Solo sincronizar si fue modificado en las últimas 48 horas
                        if (ahora_ts - os.path.getmtime(src)) <= (48 * 3600):
                            dst = os.path.join(CARPETA_DATA_CRUDA, f)
                            shutil.copy2(src, dst)
                            _log(f"Sincronizado archivo reciente desde Downloadcenter: {f}")
        except Exception as e:
            _log(f"Aviso al sincronizar Downloadcenter: {e}")


def _ejecutar_descarga(fecha_inicio: str, fecha_fin: str, es_pase_programada: bool = False, es_ultima_pasada: bool = False) -> bool:
    """
    Descarga, procesa y guarda las transacciones del rango de fechas dado.

    es_pase_programada: True cuando la llamada viene de una de las pasadas automáticas
        espaciadas del día (09:00 / 09:30 / 10:00). En ese caso, si esta pasada no trae
        marcaciones nuevas respecto al maestro acumulado, se omite el reproceso y la
        subida a Drive/GitHub (ya se hizo en una pasada anterior del mismo día).
    es_ultima_pasada: True solo en la última pasada programada del día (10:00). Si en ese
        momento la marcación más reciente sigue teniendo más de UMBRAL_ALERTA_ANTIGUEDAD_MIN
        minutos de antigüedad, se registra una alerta visible en el log.

    Retorna True si el procesamiento se ejecutó (o se omitió por no haber novedades) sin
    errores, False si ocurrió una excepción durante el procesamiento principal.
    """
    _log("=" * 60)
    # Forzar cumplimiento estricto del piso oficial de inicio de biométricos (2026-08-17)
    if fecha_inicio < FECHA_INICIO_OFICIAL:
        _log(f"Aviso: fecha_inicio {fecha_inicio} ajustada al piso oficial inviolable: {FECHA_INICIO_OFICIAL}")
        fecha_inicio = FECHA_INICIO_OFICIAL

    _log(f"Descargando transacciones del {fecha_inicio} al {fecha_fin}...")
    exito = True

    # Sincronizar descargas manuales de Downloadcenter si existen
    _sincronizar_downloadcenter()

    # Respaldo preventivo fechado de SQLite antes de cualquier procesamiento
    try:
        from data.database import crear_backup_seguridad_sqlite
        sufijo_bk = "schedule_pase" if es_pase_programada else "manual"
        crear_backup_seguridad_sqlite(sufijo=sufijo_bk)
    except Exception as e_bk:
        _log(f"Aviso al crear backup preventivo: {e_bk}")

    try:
        from core.hikvision_downloader import descargar_transacciones_hikvision
        from data.data_loader import cargar_datos_excel, fusionar_y_deduplicar_data_cruda, parse_hikvision_transaction_file
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
        _log(f"Data Cruda descargada en: {excel_path_nuevo if excel_path_nuevo else '(Sin archivo generado)'}")

        # Función auxiliar para limpieza de carpeta data_cruda
        def _limpiar_temporales_data_cruda():
            try:
                for item_tmp in os.listdir(CARPETA_DATA_CRUDA):
                    item_tmp_path = os.path.join(CARPETA_DATA_CRUDA, item_tmp)
                    if os.path.isfile(item_tmp_path) and item_tmp.strip().lower() != "transacciones_acumuladas.xlsx" and not item_tmp.startswith("~$"):
                        try:
                            os.remove(item_tmp_path)
                        except Exception:
                            pass
            except Exception:
                pass

        ruta_maestro_raw = os.path.join(CARPETA_DATA_CRUDA, "Transacciones_Acumuladas.xlsx")

        # Conteo previo a la fusión para saber si esta pasada trajo marcaciones nuevas
        conteo_previo = 0
        if os.path.exists(ruta_maestro_raw):
            try:
                df_previo = parse_hikvision_transaction_file(ruta_maestro_raw)
                conteo_previo = len(df_previo)
            except Exception:
                conteo_previo = 0

        if not excel_path_nuevo or not os.path.exists(excel_path_nuevo):
            _log("⚠️ [HikCentral] No se descargaron nuevas transacciones en este pase. Se preserva el Maestro intacto.")
            _limpiar_temporales_data_cruda()
            if es_pase_programada:
                _log("Descarga finalizada (sin cambios).")
                _log("=" * 60)
                return True
            df_marc_nuevo = pd.DataFrame()
            df_trab_nuevo = pd.DataFrame()
        else:
            # 2. Cargar y Fusionar en el Archivo Maestro de Data Cruda sin Duplicados ni Faltantes
            df_trab_nuevo, df_marc_nuevo, df_he_nuevo = cargar_datos_excel(excel_path_nuevo)

        df_marc_master = fusionar_y_deduplicar_data_cruda(df_marc_nuevo, ruta_maestro_raw)
        # Descartar estrictamente cualquier marcación anterior a la fecha de inicio oficial
        f_col = 'Fecha' if 'Fecha' in df_marc_master.columns else ('FECHA' if 'FECHA' in df_marc_master.columns else None)
        if f_col and not df_marc_master.empty:
            df_marc_master = df_marc_master[df_marc_master[f_col].astype(str) >= FECHA_INICIO_OFICIAL].copy()

        conteo_nuevo = len(df_marc_master)
        hay_marcaciones_nuevas = (conteo_nuevo > conteo_previo)

        # Antigüedad de la marcación más reciente (detecta biométrico aún sin sincronizar)
        antiguedad_min = None
        try:
            col_f = 'Fecha' if 'Fecha' in df_marc_master.columns else None
            col_t = 'Tiempo' if 'Tiempo' in df_marc_master.columns else None
            if col_f and col_t and not df_marc_master.empty:
                dt_series = pd.to_datetime(
                    df_marc_master[col_f].astype(str) + ' ' + df_marc_master[col_t].astype(str),
                    errors='coerce'
                )
                ultima_marcacion = dt_series.max()
                if pd.notna(ultima_marcacion):
                    antiguedad_min = (datetime.datetime.now() - ultima_marcacion.to_pydatetime()).total_seconds() / 60
        except Exception as e_fresh:
            _log(f"Aviso calculando antigüedad de última marcación: {e_fresh}")

        if es_pase_programada:
            msg_pase = f"Pasada programada: {conteo_previo} -> {conteo_nuevo} marcaciones acumuladas"
            if antiguedad_min is not None:
                msg_pase += f" | última marcación hace {antiguedad_min:.0f} min"
            _log(msg_pase)

            if es_ultima_pasada and antiguedad_min is not None and antiguedad_min > UMBRAL_ALERTA_ANTIGUEDAD_MIN:
                _log(f"🚨 ALERTA: tras todas las pasadas de hoy, la marcación más reciente tiene "
                     f"{antiguedad_min:.0f} min de antigüedad (umbral: {UMBRAL_ALERTA_ANTIGUEDAD_MIN} min). "
                     f"El biométrico podría no haber terminado de sincronizar con HikCentral hoy. "
                     f"Revisar manualmente o usar 'Reprocesar Datos' en la app.")

            if not hay_marcaciones_nuevas:
                _limpiar_temporales_data_cruda()
                _log("Sin marcaciones nuevas en esta pasada. Se omite reproceso, subida a Drive y sincronización con GitHub.")
                _log("Descarga finalizada (sin cambios).")
                _log("=" * 60)
                return True

        # Limpieza estricta e inmediata de cualquier descarga o reporte en downloads/data_cruda
        # para conservar ÚNICAMENTE Transacciones_Acumuladas.xlsx
        _limpiar_temporales_data_cruda()
        _log(f"Limpieza estricta de carpeta data_cruda completada. Conservando únicamente Maestro: {ruta_maestro_raw}")

        # Fallback a base de datos de trabajadores si el Excel crudo no incluye pestaña de trabajadores
        df_trab = df_trab_nuevo
        if df_trab.empty:
            from data.database import obtener_trabajadores_master
            df_trab = obtener_trabajadores_master()

        _log(f"Data Cruda Maestro Acumulada: {len(df_marc_master)} marcaciones limpias sin duplicados, {len(df_trab)} trabajadores")

        if not df_marc_master.empty:
            # Completar Posición desde maestro de trabajadores si está vacía y quitar tildes
            if not df_trab.empty:
                c_col = 'CARGO' if 'CARGO' in df_trab.columns else ('Cargo' if 'Cargo' in df_trab.columns else None)
                d_col = 'DNI' if 'DNI' in df_trab.columns else None
                if c_col and d_col:
                    cargo_dict = dict(zip(df_trab[d_col].astype(str).str.strip().str.zfill(8), df_trab[c_col].astype(str).str.strip()))
                    pos_col = 'Posición' if 'Posición' in df_marc_master.columns else ('Posicion' if 'Posicion' in df_marc_master.columns else None)
                    id_col = 'ID' if 'ID' in df_marc_master.columns else 'DNI'
                    if pos_col and id_col:
                        for r_idx, r_val in df_marc_master.iterrows():
                            cur_p = str(r_val.get(pos_col, '')).strip()
                            d_id = str(r_val.get(id_col, '')).strip().zfill(8)
                            if (not cur_p or cur_p.lower() in ('nan', 'none', '', '-')) and d_id in cargo_dict:
                                df_marc_master.loc[r_idx, pos_col] = cargo_dict[d_id]

            from data.exporter import quitar_tildes
            for col_name in ['Nombre', 'Apellido', 'Nombres', 'Apellidos']:
                if col_name in df_marc_master.columns:
                    df_marc_master[col_name] = df_marc_master[col_name].astype(str).apply(quitar_tildes)

            # Guardar el Archivo Maestro de Data Cruda en Excel usando data.exporter
            try:
                from data.exporter import guardar_transacciones_acumuladas_excel
                guardar_transacciones_acumuladas_excel(df_marc_master, ruta_maestro_raw)
                _log(f"Archivo Maestro Data Cruda guardado con formato corporativo unificado en: {ruta_maestro_raw}")
            except Exception as e_m:
                _log(f"Aviso guardando maestro data cruda: {e_m}")

            # Guardar y Subir Data Cruda Maestro (Transacciones_Acumuladas.xlsx) a Google Drive (directo a carpeta AGOSTO)
            subir_archivo_a_gdrive(ruta_maestro_raw)
            guardar_marcaciones_raw(df_marc_master, archivo_origen=ruta_maestro_raw)
            if not df_trab.empty:
                guardar_trabajadores(df_trab)
                df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc_master)
                guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)
                
                # 3. Guardar Reporte Consolidado Período Completo en la raíz y en data_procesada (localmente)
                guardar_excel_base(df_trab, df_marc_master, df_asis, df_he_out, df_inc)
                _log(f"Procesamiento consolidado completado. Guardado en carpeta raíz y downloads/data_procesada/.")

                # 4. Generar y Subir a Google Drive ÚNICAMENTE los Reportes Procesados Diarios de Días Cerrados (directo a carpeta AGOSTO)
                carp_diario = os.path.join(CARPETA_DATA_PROCESADA, "diario")
                os.makedirs(carp_diario, exist_ok=True)

                hoy_str = datetime.date.today().strftime("%Y-%m-%d")
                ayer_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

                if 'FECHA' in df_asis.columns:
                    # Generar y Subir a Google Drive ÚNICAMENTE el reporte del DÍA RECIÉN CERRADO (AYER)
                    df_asis_dia = df_asis[df_asis['FECHA'].astype(str) == ayer_str]
                    if not df_asis_dia.empty:
                        file_name_dia = f"Reporte_Asistencia_GZG_{ayer_str}.xlsx"
                        
                        # Subcarpeta por mes en PC local (ej. downloads/data_procesada/diario/agosto o setiembre)
                        mes_ayer = ayer_str.split("-")[1] if "-" in ayer_str else "08"
                        mapa_meses = {
                            "01": "enero", "02": "febrero", "03": "marzo", "04": "abril",
                            "05": "mayo", "06": "junio", "07": "julio", "08": "agosto",
                            "09": "setiembre", "10": "octubre", "11": "noviembre", "12": "diciembre"
                        }
                        nombre_subcarpeta = mapa_meses.get(mes_ayer, f"mes_{mes_ayer}")
                        carp_diario_mes = os.path.join(carp_diario, nombre_subcarpeta)
                        os.makedirs(carp_diario_mes, exist_ok=True)

                        file_path_dia = os.path.join(carp_diario_mes, file_name_dia)

                        excel_bytes = exportar_asistencia_excel(df_trab, df_marc_master, df_asis_dia, df_he_out, df_inc)
                        try:
                            with open(file_path_dia, "wb") as f_out:
                                f_out.write(excel_bytes)
                            _log(f"Reporte diario recién cerrado generado para {ayer_str} -> {file_path_dia}")
                            subir_archivo_a_gdrive(file_path_dia)
                        except PermissionError:
                            ts_str = datetime.datetime.now().strftime("%H%M%S")
                            file_path_alt = os.path.join(carp_diario_mes, f"Reporte_Asistencia_GZG_{ayer_str}_{ts_str}.xlsx")
                            with open(file_path_alt, "wb") as f_out:
                                f_out.write(excel_bytes)
                            _log(f"Aviso: {file_name_dia} abierto en Excel. Guardado copia -> {file_path_alt}")
                            subir_archivo_a_gdrive(file_path_alt)
                    else:
                        _log(f"Aviso: No se encontraron registros de asistencia para el día cerrado {ayer_str}.")
                
                # 4.5 Sincronizar y Regenerar Aprobaciones mensuales y subir a Google Drive
                try:
                    from data.database import sincronizar_aprobaciones_desde_asistencia, sincronizar_aprobaciones_con_gdrive, DB_PATH, get_connection
                    from data.exporter import exportar_aprobaciones_excel
                    
                    # 1. Rehidratar PRIMERO desde Google Drive para absorber aprobaciones hechas en Streamlit Cloud
                    sincronizar_aprobaciones_con_gdrive(DB_PATH)
                    
                    # 2. Agregar únicamente nuevos días cerrados sin tocar los existentes (fecha <= ayer_str)
                    sincronizar_aprobaciones_desde_asistencia(DB_PATH, fecha_max=ayer_str)
                    
                    conn_ap = get_connection(DB_PATH)
                    df_aprob_all = pd.read_sql_query(
                        "SELECT * FROM aprobaciones WHERE fecha >= '2026-08-17' AND fecha <= ? ORDER BY fecha DESC, id DESC",
                        conn_ap,
                        params=[ayer_str]
                    )
                    conn_ap.close()
                    
                    if not df_aprob_all.empty and 'fecha' in df_aprob_all.columns:
                        meses_presentes = sorted(df_aprob_all['fecha'].astype(str).str[:7].dropna().unique())
                        for m_str in meses_presentes:
                            if len(m_str) == 7 and m_str.startswith("20"):
                                df_aprob_mes = df_aprob_all[df_aprob_all['fecha'].astype(str).str.startswith(m_str)]
                                if not df_aprob_mes.empty:
                                    aprob_path_mes = os.path.join(CARPETA_DATA_PROCESADA, f"Aprobaciones_GZG_{m_str}.xlsx")
                                    if exportar_aprobaciones_excel(df_aprob_mes, aprob_path_mes):
                                        subir_archivo_a_gdrive(aprob_path_mes)
                                        _log(f"Aprobaciones del mes {m_str} ({aprob_path_mes}) generadas y subidas a Google Drive con éxito.")
                except Exception as e_aprob:
                    _log(f"Aviso actualizando aprobaciones en schedule: {e_aprob}")

                # Actualizar únicamente de forma local en la PC el archivo raíz principal Sistema_Asistencia_GZG_v1.0.xlsx
                ruta_root_v1 = os.path.join(ROOT_DIR, "Sistema_Asistencia_GZG_v1.0.xlsx")
                excel_bytes_root = exportar_asistencia_excel(df_trab, df_marc_master, df_asis, df_he_out, df_inc)
                try:
                    with open(ruta_root_v1, "wb") as f_out:
                        f_out.write(excel_bytes_root)
                    _log(f"Archivo raíz principal actualizado en PC local: {ruta_root_v1}")
                except Exception as e_v1:
                    _log(f"Aviso actualizando archivo raíz principal local: {e_v1}")
            else:
                _log("AVISO: No se encontraron trabajadores en la base de datos para procesar asistencia.")
        else:
            _log("AVISO: No se encontraron marcaciones en el archivo.")

    except Exception as e:
        import traceback
        _log(f"ERROR: {e}")
        _log(traceback.format_exc())
        exito = False

    # 5. Sincronización Automática con GitHub para Streamlit Cloud
    try:
        _log("Sincronizando cambios diarios con GitHub / Streamlit Cloud...")
        subprocess.run(["git", "add", "data/asistencia.db", "downloads/data_procesada/", "Padron_Trabajadores_GZG.xlsx"], cwd=ROOT_DIR, check=False)
        subprocess.run(["git", "commit", "-m", "auto: Daily attendance & approvals update 9AM"], cwd=ROOT_DIR, check=False)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT_DIR, check=True)
        _log("[OK] Sincronizado exitosamente con GitHub.")
    except Exception as e_git:
        _log(f"Aviso en sincronización git: {e_git}")

    _log("Descarga finalizada.")
    _log("=" * 60)
    return exito


def reprocesar_fecha(fecha_str: str, fecha_inicio_base: str = "2026-08-17") -> bool:
    """
    Reproceso manual bajo demanda para una fecha específica (pensado para ser llamado
    desde la app, ej. un botón de administración). Siempre corre completo —no aplica
    la lógica de "omitir si no hay novedades" de las pasadas programadas— porque es
    una acción explícita del usuario.
    """
    _log(f"Reproceso MANUAL solicitado desde la app para: {fecha_str}")
    return _ejecutar_descarga(fecha_inicio_base, fecha_str, es_pase_programada=False, es_ultima_pasada=False)


def _hoy() -> str:
    return datetime.date.today().strftime("%Y-%m-%d")


def _ayer() -> str:
    return (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")


def _fecha_inicio_acumulado() -> str:
    """
    Fecha de inicio del acumulado oficial de transacciones.
    Los biométricos iniciaron operaciones oficiales el 2026-08-17.
    Regla estricta: NUNCA descargar ni acumular datos previos a esta fecha.
    """
    return FECHA_INICIO_OFICIAL


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
        _ejecutar_descarga("2026-08-17", fecha)

    elif opcion == "2":
        fecha = _ayer()
        print(f"\n  Descargando AYER: {fecha}")
        _ejecutar_descarga("2026-08-17", fecha)

    elif opcion == "3":
        fecha_str = input("  Ingrese la fecha (DD/MM/YYYY, YYYY-MM-DD o YYYY/MM/DD): ").strip()
        fecha = _parsear_fecha(fecha_str)
        if fecha:
            print(f"\n  Descargando: {fecha}")
            _ejecutar_descarga("2026-08-17", fecha)
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
            if ini < FECHA_INICIO_OFICIAL:
                print(f"  Aviso: fecha inicio ajustada al piso oficial: {FECHA_INICIO_OFICIAL}")
                ini = FECHA_INICIO_OFICIAL
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
    """Servicio que ejecuta 3 pasadas matutinas espaciadas (09:00, 09:30 y 10:00 AM)."""
    try:
        import schedule
    except ImportError:
        os.system(f'"{sys.executable}" -m pip install schedule')
        import schedule

    _log("Servicio de descarga diaria iniciado.")
    _log(f"  Horario    : 3 pasadas espaciadas por día -> 09:00, 09:30 y 10:00 AM")
    _log(f"  Motivo     : el biométrico físico puede tardar en sincronizar sus eventos")
    _log(f"               offline con el servidor HikCentral; el merge es idempotente,")
    _log(f"               así que reintentar en pasadas espaciadas es más confiable que")
    _log(f"               reintentos apretados dentro de la misma ejecución.")
    _log(f"  Descarga   : acumulado desde 2026-08-17 hasta HOY en cada pasada")
    _log(f"  Data Cruda : {CARPETA_DATA_CRUDA}")
    _log(f"  Procesada  : {CARPETA_DATA_PROCESADA}")
    _log(f"  Log        : {LOG_FILE}")

    def _tarea_programada(es_ultima: bool = False):
        ini = _fecha_inicio_acumulado()
        _log(f"Tarea programada: descargando acumulado desde {ini} hasta {_hoy()}"
             + (" [ÚLTIMA PASADA DEL DÍA]" if es_ultima else ""))
        _ejecutar_descarga(ini, _hoy(), es_pase_programada=True, es_ultima_pasada=es_ultima)

    schedule.every().day.at("09:00").do(lambda: _tarea_programada(es_ultima=False))
    schedule.every().day.at("09:30").do(lambda: _tarea_programada(es_ultima=False))
    schedule.every().day.at("10:00").do(lambda: _tarea_programada(es_ultima=True))

    while True:
        schedule.run_pending()
        time.sleep(30)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    args = sys.argv[1:]

    if not args or args[0].lower() in ("ahora", "now", "auto", "automatico"):
        # Modo por defecto (ejecución manual inmediata, sin la lógica de "omitir si no hay
        # novedades" de las pasadas programadas): siempre procesa completo.
        ini = _fecha_inicio_acumulado()
        fin = _hoy()
        _log(f"Ejecución MANUAL/INMEDIATA: descargando acumulado {ini} -> {fin} para emparejamiento completo de Turno Noche...")
        _ejecutar_descarga(ini, fin)

    elif args[0].lower() in ("pase1", "pase09", "pase_0900"):
        # Para usar con 3 Tareas Programadas de Windows separadas (09:00/09:30/10:00)
        # en vez del modo "daemon". Esta es la 1ra pasada del daí.
        _log("Ejecución PROGRAMADA - Pasada 1/3 (09:00 AM)")
        _ejecutar_descarga(_fecha_inicio_acumulado(), _hoy(), es_pase_programada=True, es_ultima_pasada=False)

    elif args[0].lower() in ("pase2", "pase0930", "pase_0930"):
        # 2da pasada del día (09:30 AM)
        _log("Ejecución PROGRAMADA - Pasada 2/3 (09:30 AM)")
        _ejecutar_descarga(_fecha_inicio_acumulado(), _hoy(), es_pase_programada=True, es_ultima_pasada=False)

    elif args[0].lower() in ("pase3", "pase_final", "pasefinal", "pase1000"):
        # Última pasada del día (10:00 AM) — aquí se dispara la alerta de antigüedad si aplica
        _log("Ejecución PROGRAMADA - Pasada 3/3 FINAL (10:00 AM)")
        _ejecutar_descarga(_fecha_inicio_acumulado(), _hoy(), es_pase_programada=True, es_ultima_pasada=True)

    elif args[0].lower() in ("daemon", "service", "servicio"):
        # Modo servicio continuo 24/7 (bucle)
        _iniciar_programador()

    elif args[0].lower() == "manual":
        # Menú interactivo para elegir fecha
        _menu_manual()

    elif len(args) == 1 and _parsear_fecha(args[0]):
        # Fecha específica como argumento: python schedule_downloader.py 2026-08-17
        fecha = _parsear_fecha(args[0])
        fecha = max(fecha, FECHA_INICIO_OFICIAL)
        _log(f"Ejecución MANUAL con fecha: {fecha}")
        _ejecutar_descarga(fecha, fecha)

    elif len(args) == 2 and _parsear_fecha(args[0]) and _parsear_fecha(args[1]):
        # Rango: python schedule_downloader.py 2026-08-15 2026-08-17
        ini = _parsear_fecha(args[0])
        fin = _parsear_fecha(args[1])
        if ini > fin:
            ini, fin = fin, ini
        ini = max(ini, FECHA_INICIO_OFICIAL)
        _log(f"Ejecución MANUAL con rango: {ini} -> {fin}")
        _ejecutar_descarga(ini, fin)

    else:
        print(__doc__)
