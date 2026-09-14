@echo off
title Sincronizar Aprobaciones GZG desde Google Drive
color 0B
echo ======================================================================
echo    GZG MINERALES - SINCRONIZADOR DE APROBACIONES DE HORAS EXTRAS
echo ======================================================================
echo.
echo  Consultando Google Drive y descargando estados actualizados...
echo.
cd /d "%~dp0"
python scripts/auto_sync_approvals.py --once
echo.
echo ======================================================================
echo  Proceso completado. El archivo Excel local en downloads/data_procesada
echo  ha sido actualizado con la ultima version de Google Drive.
echo ======================================================================
echo.
pause
