@echo off
title GZG - Instalador Tarea Programada 8AM
cd /d "%~dp0"

echo.
echo  ============================================================
echo   GZG - DESCARGA AUTOMATICA DIARIA (8:00 AM)
echo  ============================================================
echo  Directorio: %CD%
echo.
echo  IMPORTANTE: Si no funciona, ejecute como ADMINISTRADOR
echo  (clic derecho sobre este archivo ^> Ejecutar como administrador)
echo.

:: Verificar Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python no encontrado. Instale Python desde python.org
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

echo  Python    : %PYTHON_EXE%
echo  Script    : %SCRIPT_PATH%
echo  Tarea     : %TASK_NAME%
echo  Horario   : 08:00 AM diario (descarga el dia anterior)
echo.

:: Verificar que el script existe
if not exist "%SCRIPT_PATH%" (
    echo  [ERROR] No se encuentra el script:
    echo  %SCRIPT_PATH%
    pause
    exit /b 1
)

:: Eliminar tarea anterior si existe
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Crear tarea programada
schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" /sc DAILY /st 08:00 /ru "%USERNAME%" /rl HIGHEST /f

if %errorlevel% equ 0 (
    echo.
    echo  [OK] Tarea creada correctamente!
    echo.
    echo  Archivos descargados: %PROJECT_DIR%\downloads\hikvision\
    echo  Log de ejecuciones  : %PROJECT_DIR%\logs\descarga_diaria.log
    echo.
    echo  Para verificar: Inicio ^> Programador de Tareas ^> %TASK_NAME%
) else (
    echo.
    echo  [ERROR] No se pudo crear la tarea.
    echo  Intente clic derecho ^> "Ejecutar como administrador"
)

echo.
pause
