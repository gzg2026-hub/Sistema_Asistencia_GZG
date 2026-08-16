@echo off
title Sistema de Asistencia GZG
echo ========================================================
echo   INICIANDO SISTEMA DE ASISTENCIA Y CONTROL DE TIEMPOS
echo ========================================================
echo.
cd /d "%~dp0"
python -m streamlit run app.py
pause
