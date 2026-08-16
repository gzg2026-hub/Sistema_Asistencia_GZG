import os
import sys
import time
import schedule
import datetime

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hikvision_downloader import descargar_transacciones_hikvision
from data.data_loader import cargar_datos_excel
from core.attendance_engine import procesar_asistencia_df
from data.database import guardar_trabajadores, guardar_marcaciones_raw, guardar_asistencia_y_reportes
from data.exporter import guardar_excel_base

def ejecucion_diaria_8am():
    print(f"[{datetime.datetime.now()}] Iniciando descarga y procesamiento automatico de 8:00 AM...")
    try:
        # 1. Descargar transacciones de Hikvision
        excel_descargado = descargar_transacciones_hikvision()
        print(f"Descarga completada en: {excel_descargado}")
        
        # 2. Cargar datos
        df_trab, df_marc, df_he = cargar_datos_excel(excel_descargado)
        
        if not df_marc.empty:
            # 3. Guardar marcaciones raw en SQLite
            guardar_marcaciones_raw(df_marc, archivo_origen=excel_descargado)
            
            # 4. Procesar asistencia
            if not df_trab.empty:
                guardar_trabajadores(df_trab)
                df_asis, df_he_out, df_inc, kpis = procesar_asistencia_df(df_trab, df_marc)
                
                # 5. Guardar en SQLite
                guardar_asistencia_y_reportes(df_asis, df_he_out, df_inc)
                
                # 6. Rellenar Excel base v1.0
                guardar_excel_base(df_trab, df_marc, df_asis, df_he_out, df_inc)
                print(f"Procesamiento automatico de 8:00 AM completado con exito. Total marcaciones: {len(df_marc)}")
    except Exception as e:
        print(f"Error durante el procesamiento automatico de 8:00 AM: {e}")

def iniciar_programador():
    print("Iniciando servicio de descarga diaria de Hikvision a las 8:00 AM (Lunes a Domingo)...")
    schedule.every().day.at("08:00").do(ejecucion_diaria_8am)
    
    # Ejecución inicial de prueba
    # ejecucion_diaria_8am()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    iniciar_programador()
