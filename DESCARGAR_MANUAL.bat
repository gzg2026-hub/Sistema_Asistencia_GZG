@echo off
title GZG - Descarga Manual Hikvision
cd /d "%~dp0\.."
echo.
echo  =========================================
echo   GZG - DESCARGA MANUAL DE TRANSACCIONES
echo  =========================================
echo.
python scripts\schedule_downloader.py manual
