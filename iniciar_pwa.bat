@echo off
title Servidor PWA GZG Minerales - Control de Asistencia y Aprobaciones
echo ======================================================================
echo    INICIANDO SERVIDOR PWA MÓVIL Y DE ESCRITORIO - GZG MINERALES
echo ======================================================================
echo.
echo   La aplicación estará disponible para instalar en:
echo   - Localmente: http://localhost:8501
echo   - Desde Celular en Wi-Fi: http://%COMPUTERNAME%:8501
echo.
echo ======================================================================
echo.
cd /d "%~dp0"
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
pause
