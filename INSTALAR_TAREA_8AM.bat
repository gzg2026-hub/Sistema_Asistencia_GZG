@echo off
title GZG - Instalador Tarea Programada 7AM
echo.
echo  ============================================================
echo   GZG - INSTALACION DE DESCARGA AUTOMATICA DIARIA (7:00 AM)
echo  ============================================================
echo.
echo  Este script crea una Tarea Programada en Windows para que
echo  la descarga de Hikvision se ejecute AUTOMATICAMENTE todos
echo  los dias a las 07:00 AM (descarga el dia anterior).
echo.
echo  REQUISITO: ejecutar como ADMINISTRADOR.
echo.

:: Obtener la ruta del proyecto (un nivel arriba del .bat)
set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

:: Buscar python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instale Python primero.
    pause
    exit /b 1
)
for /f "delims=" %%i in ('where python') do set "PYTHON_EXE=%%i" & goto :found_python
:found_python

set "SCRIPT_PATH=%PROJECT_DIR%\scripts\schedule_downloader.py"
set "TASK_NAME=GZG_Hikvision_Descarga_8AM"

echo  Python encontrado: %PYTHON_EXE%
echo  Script           : %SCRIPT_PATH%
echo  Tarea            : %TASK_NAME%
echo  Hora programada  : 08:00 AM (diario)
echo.

:: Eliminar tarea anterior si existe
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Crear nueva tarea programada
schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" ^
  /sc DAILY ^
  /st 08:00 ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f

if %errorlevel% equ 0 (
    echo.
    echo  [OK] Tarea programada creada exitosamente.
    echo  Los archivos se guardaran en:
    echo    %PROJECT_DIR%\downloads\hikvision\
    echo  Los logs se guardan en:
    echo    %PROJECT_DIR%\logs\descarga_diaria.log
    echo.
    echo  Para verificar: Abrir "Programador de Tareas" de Windows
    echo  y buscar la tarea: %TASK_NAME%
) else (
    echo.
    echo  [ERROR] No se pudo crear la tarea.
    echo  Intente ejecutar este archivo como ADMINISTRADOR (clic derecho ^> Ejecutar como admin).
)

echo.
pause
