@echo off
title GZG - Instalador Tarea Programada 8AM
cd /d "%~dp0"

echo.
echo  ============================================================
echo   GZG - DESCARGA AUTOMATICA DIARIA HIKVISION (8:00 AM)
echo  ============================================================
echo  Directorio: %CD%
echo.
echo  IMPORTANTE: Clic derecho sobre este archivo ^> "Ejecutar como administrador"
echo.

:: Verificar Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python no encontrado en el sistema.
    pause
    exit /b 1
)
for /f "delims=" %%i in ('where python') do (
    set "PYTHON_EXE=%%i"
    goto :found_python
)
:found_python

set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

set "SCRIPT_PATH=%PROJECT_DIR%\scripts\schedule_downloader.py"
set "TASK_NAME=GZG_Hikvision_Descarga_8AM"

echo  Python EXE : %PYTHON_EXE%
echo  Script     : %SCRIPT_PATH%
echo  Tarea Name : %TASK_NAME%
echo  Horario    : 08:00 AM diario (descarga el día anterior)
echo  Recuperación: SI LA PC ESTÁ APAGADA A LAS 8AM, SE EJECUTA AUTOMÁTICAMENTE AL ENCENDER
echo.

if not exist "%SCRIPT_PATH%" (
    echo  [ERROR] No se encuentra el script: %SCRIPT_PATH%
    pause
    exit /b 1
)

:: Registrar tarea en Windows usando PowerShell con StartWhenAvailable=true
powershell -Command "$action = New-ScheduledTaskAction -Execute '%PYTHON_EXE%' -Argument '\"%SCRIPT_PATH%\" ahora' -WorkingDirectory '%PROJECT_DIR%'; $trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM; $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries; Register-ScheduledTask -TaskName '%TASK_NAME%' -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force" >nul 2>&1

if %errorlevel% equ 0 (
    echo.
    echo  [OK] ¡Tarea programada registrada con éxito!
    echo.
    echo  - Hora de ejecución diaria : 08:00 AM
    echo  - Si la PC estaba apagada : Se ejecutará AUTOMÁTICAMENTE apenas enciendas la PC.
    echo  - Archivos guardados en   : %PROJECT_DIR%\downloads\hikvision\
    echo  - Log de ejecuciones     : %PROJECT_DIR%\logs\descarga_diaria.log
    echo.
) else (
    echo.
    echo  [ERROR] No se pudo crear la tarea. Asegúrese de ejecutar como Administrador.
)

echo.
pause
