import subprocess

py = r'C:\Users\GZG Minerales 2026\AppData\Local\Python\pythoncore-3.14-64\python.exe'
script = r'C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scripts\schedule_downloader.py'
cwd = r'C:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG'

tasks = [
    ("GZG_Hikvision_Descarga_Diaria_9AM", "pase1", "09:00"),
    ("GZG_Hikvision_Descarga_Diaria_930AM", "pase2", "09:30"),
    ("GZG_Hikvision_Descarga_Diaria_10AM", "pase3", "10:00")
]

ps_script = f"""
$py = '{py}'
$script = '{script}'
$cwd = '{cwd}'

$tasks = @(
    @{{ Name = 'GZG_Hikvision_Descarga_Diaria_9AM'; Arg = 'pase1'; Time = '09:00' }},
    @{{ Name = 'GZG_Hikvision_Descarga_Diaria_930AM'; Arg = 'pase2'; Time = '09:30' }},
    @{{ Name = 'GZG_Hikvision_Descarga_Diaria_10AM'; Arg = 'pase3'; Time = '10:00' }}
)

foreach ($t in $tasks) {{
    $action = New-ScheduledTaskAction -Execute $py -Argument ('"' + $script + '" ' + $t.Arg) -WorkingDirectory $cwd
    $trigger = New-ScheduledTaskTrigger -Daily -At $t.Time
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    Register-ScheduledTask -TaskName $t.Name -Action $action -Trigger $trigger -Settings $settings -Force
    Write-Host ("Registrada con exito: " + $t.Name + " a las " + $t.Time)
}}
"""

res = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print("Returncode:", res.returncode)
