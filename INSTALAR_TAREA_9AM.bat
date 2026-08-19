@echo off
title GZG - Instalador Tarea Programada 9AM
cd /d "%~dp0"

echo.
echo  ============================================================
echo   GZG - DESCARGA AUTOMATICA DIARIA HIKVISION (9:00 AM)
echo  ============================================================
echo  Directorio  : %CD%
echo  Python EXE  : C:\Users\GZG Minerales 2026\AppData\Local\Python\pythoncore-3.14-64\python.exe
echo  Script      : %CD%\scripts\schedule_downloader.py
echo  Tarea Name  : GZG_Hikvision_Descarga_Diaria_9AM
echo  Horario     : 09:00 AM diario (descarga el dia anterior)
echo  Recuperacion: SI LA PC ESTA APAGADA A LAS 9AM, SE EJECUTA AUTOMATICAMENTE AL ENCENDER
echo  ============================================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0scripts\register_task_9am.ps1"
if %errorlevel% equ 0 goto exito
goto error

:exito
echo.
echo  ============================================================
echo   [OK] ¡TAREA PROGRAMADA REGISTRADA CON EXITO A LAS 9:00 AM!
echo  ============================================================
echo   - Horario Diario          : 09:00 AM
echo   - Recuperacion al encender: ACTIVA (si la PC estaba apagada)
echo   - Carpeta Data Cruda      : %CD%\downloads\data_cruda\
echo   - Carpeta Data Procesada  : %CD%\downloads\data_procesada\
echo   - Log de Ejecucion        : %CD%\logs\descarga_diaria.log
echo  ============================================================
goto fin

:error
echo.
echo  ============================================================
echo   [ERROR] No se pudo crear la tarea programada.
echo   Asegúrese de hacer clic derecho sobre INSTALAR_TAREA_9AM.bat
echo   y seleccionar: "Ejecutar como administrador".
echo  ============================================================
goto fin

:fin
echo.
echo  Presione cualquier tecla para cerrar esta ventana...
pause >nul
