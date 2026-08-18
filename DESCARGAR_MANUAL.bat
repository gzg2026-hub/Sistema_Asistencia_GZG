@echo off
title GZG - Descarga Manual Hikvision
cd /d "%~dp0"

echo.
echo  =========================================
echo   GZG - DESCARGA MANUAL DE TRANSACCIONES
echo  =========================================
echo  Directorio: %CD%
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python no encontrado en PATH.
    echo  Instale Python desde python.org
    pause
    exit /b 1
)

python scripts\schedule_downloader.py manual
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] El script termino con error.
    pause
)
