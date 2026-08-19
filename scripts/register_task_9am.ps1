$ErrorActionPreference = "Stop"

try {
    $py = "C:\Users\GZG Minerales 2026\AppData\Local\Python\pythoncore-3.14-64\python.exe"
    $script = "C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scripts\schedule_downloader.py"
    $dir = "C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"

    Unregister-ScheduledTask -TaskName "GZG_Hikvision_Descarga_8AM" -Confirm:$False -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "GZG_Hikvision_Descarga_Diaria_8AM" -Confirm:$False -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName "GZG_Hikvision_Descarga_Diaria_9AM" -Confirm:$False -ErrorAction SilentlyContinue

    $action = New-ScheduledTaskAction -Execute $py -Argument "`"$script`" ahora" -WorkingDirectory $dir
    $trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    Register-ScheduledTask -TaskName "GZG_Hikvision_Descarga_Diaria_9AM" -Action $action -Trigger $trigger -Settings $settings -Force > $null
    exit 0
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
