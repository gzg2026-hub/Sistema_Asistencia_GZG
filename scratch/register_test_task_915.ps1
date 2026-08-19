$py = "C:\Users\GZG Minerales 2026\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$script = "C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scripts\schedule_downloader.py"
$dir = "C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"

$action = New-ScheduledTaskAction -Execute $py -Argument "`"$script`" ahora" -WorkingDirectory $dir
$trigger = New-ScheduledTaskTrigger -Once -At 9:15AM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "GZG_Hikvision_Descarga_Test_915" -Action $action -Trigger $trigger -Settings $settings -User "GZG Minerales 2026" -Force
