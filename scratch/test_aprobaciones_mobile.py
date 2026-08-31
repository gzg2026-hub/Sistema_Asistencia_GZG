import os
import sys

PROJECT_ROOT = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG"
sys.path.insert(0, PROJECT_ROOT)

from data.database import sincronizar_aprobaciones_desde_asistencia, obtener_solicitudes_aprobacion

print("=== PRUEBA SINCRO Y CONSULTA APROBACIONES MÓVIL ===")
sincronizar_aprobaciones_desde_asistencia()

df_sol = obtener_solicitudes_aprobacion('TODAS')
print(f"Total solicitudes cargadas en aprobaciones: {len(df_sol)}")
print(df_sol[['id', 'fecha', 'dni', 'apellidos', 'nombres', 'cargo', 'horas_extras_hhmm', 'exceso_jornada_hhmm', 'estado']].head(10))
