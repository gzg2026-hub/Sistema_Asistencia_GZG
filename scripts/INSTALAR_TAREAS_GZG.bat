@echo off
title GZG - Instalador Tareas Programadas (3 Pasadas)
cd /d "%~dp0.."

echo.
echo  ============================================================
echo   GZG - INSTALADOR TAREAS AUTOMATICAS HIKVISION
echo   3 Pasadas: 09:00 (pase1) / 09:30 (pase2) / 10:00 (pase3)
echo  ============================================================
echo  EJECUTAR COMO ADMINISTRADOR
echo  ============================================================
echo.

set PYTHON=C:\Users\GZG Minerales 2026\AppData\Local\Python\pythoncore-3.14-64\python.exe
set SCRIPT=C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scripts\schedule_downloader.py
set WORKDIR=C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG

echo [1/3] Instalando tarea 09:00 AM (pase1)...
schtasks /Delete /TN "GZG_Hikvision_Descarga_Diaria_9AM" /F 2>nul
schtasks /Create /TN "GZG_Hikvision_Descarga_Diaria_9AM" /SC DAILY /ST 09:00 /F /RL HIGHEST /RU "GZG Minerales 2026" /TR "\"%PYTHON%\" \"%SCRIPT%\" pase1"
echo.

echo [2/3] Instalando tarea 09:30 AM (pase2)...
schtasks /Delete /TN "GZG_Hikvision_Descarga_Diaria_930AM" /F 2>nul
schtasks /Create /TN "GZG_Hikvision_Descarga_Diaria_930AM" /SC DAILY /ST 09:30 /F /RL HIGHEST /RU "GZG Minerales 2026" /TR "\"%PYTHON%\" \"%SCRIPT%\" pase2"
echo.

echo [3/3] Instalando tarea 10:00 AM (pase3 - ultima pasada)...
schtasks /Delete /TN "GZG_Hikvision_Descarga_Diaria_10AM" /F 2>nul
schtasks /Create /TN "GZG_Hikvision_Descarga_Diaria_10AM" /SC DAILY /ST 10:00 /F /RL HIGHEST /RU "GZG Minerales 2026" /TR "\"%PYTHON%\" \"%SCRIPT%\" pase3"
echo.

echo  ============================================================
echo   VERIFICACION FINAL
echo  ============================================================
schtasks /query /fo TABLE /nh | findstr "GZG_Hikvision"
echo.
echo  Listo. Las 3 tareas estan activas.
pause
