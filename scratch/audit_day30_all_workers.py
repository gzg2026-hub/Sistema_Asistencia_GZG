import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
import openpyxl

raw = pd.read_excel('downloads/data_cruda/Transacciones_Acumuladas.xlsx')
raw['DNI_NORM'] = raw['ID'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).apply(lambda d: str(d).lstrip('0').zfill(8))

rep = pd.read_excel('downloads/data_procesada/diario/Reporte_Asistencia_GZG_2026-08-30.xlsx', header=3)
rep['DNI_NORM'] = rep['DNI'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).apply(lambda d: str(d).lstrip('0').zfill(8))

print("=" * 90)
print("AUDITORÍA INTEGRAL DE TODAS LAS PERSONAS PARA EL DÍA 30 DE AGOSTO DE 2026")
print("=" * 90)

# Check all DNIs that had swipes on 2026-08-30
dnis_swipes_30 = sorted(raw[raw['Fecha'] == '2026-08-30']['DNI_NORM'].unique())
print(f"Total trabajadores con marcaciones el 30/08: {len(dnis_swipes_30)}")
print(f"Total filas generadas en el reporte del 30/08: {len(rep)}")

anomalias = []
relevos = []
normales = []

for dni in dnis_swipes_30:
    sub_raw_30 = raw[(raw['DNI_NORM'] == dni) & (raw['Fecha'].isin(['2026-08-30', '2026-08-31']))].sort_values(['Fecha', 'Tiempo'])
    nombre = f"{sub_raw_30.iloc[0]['Apellido']} {sub_raw_30.iloc[0]['Nombre']}"
    sub_rep = rep[rep['DNI_NORM'] == dni]
    
    swipes_summary = " | ".join([f"{r['Fecha']} {r['Tiempo']} ({r['Tipo de pase de tarjeta']})" for _, r in sub_raw_30.iterrows()])
    
    if sub_rep.empty:
        anomalias.append({
            'DNI': dni,
            'Nombre': nombre,
            'Problema': 'TIENE MARCACIONES EL 30/08 PERO NO APARECE EN EL REPORTE',
            'Swipes': swipes_summary
        })
        continue
        
    for _, r_rep in sub_rep.iterrows():
        turno = str(r_rep.get('Turno', ''))
        h_ent = str(r_rep.get('Hora Entrada', ''))
        h_sal = str(r_rep.get('Hora Salida', ''))
        h_turno = str(r_rep.get('Horas de Turno', ''))
        tipo_reg = str(r_rep.get('Tipo Registro', ''))
        obs = str(r_rep.get('Observación / Incidencias', ''))
        
        # Check if there are unclosed shifts or unexpected issues
        is_anom = False
        problemas = []
        
        if pd.isna(r_rep.get('Hora Entrada')) or h_ent in ('nan', '-', '', 'None'):
            is_anom = True
            problemas.append("Falta Entrada")
        if pd.isna(r_rep.get('Hora Salida')) or h_sal in ('nan', '-', '', 'None'):
            is_anom = True
            problemas.append("Falta Salida")
        if 'Salida anticipada' in obs:
            is_anom = True
            problemas.append(f"Salida Anticipada ({obs})")
            
        row_info = {
            'DNI': dni,
            'Nombre': nombre,
            'Turno': turno,
            'Horario': f"{h_ent} -> {h_sal} ({h_turno})",
            'Tipo': tipo_reg,
            'Obs': obs,
            'Swipes': swipes_summary
        }
        
        if is_anom:
            row_info['Problemas'] = ", ".join(problemas)
            anomalias.append(row_info)
        elif tipo_reg == 'Cambio de guardia' or 'Jornada parcial' in obs:
            relevos.append(row_info)
        else:
            normales.append(row_info)

print("\n" + "=" * 90)
print(f"1. CASOS CON ANOMALÍAS O ALERTAS (Total: {len(anomalias)})")
print("=" * 90)
if anomalias:
    for a in anomalias:
        print(f"\n[ALERTA] DNI: {a['DNI']} - {a['Nombre']}")
        print(f"  Turno: {a.get('Turno', '')} | Evaluado: {a.get('Horario', '')} | Tipo: {a.get('Tipo', '')}")
        print(f"  Observación: {a.get('Obs', '')} | Problema: {a.get('Problemas', a.get('Problema', ''))}")
        print(f"  Marcaciones crudas: {a['Swipes']}")
else:
    print("  >> NINGUNA ANOMALÍA ENCONTRADA. Todos los turnos cerraron limpiamente.")

print("\n" + "=" * 90)
print(f"2. CASOS DE CAMBIO DE GUARDIA / MEDIA JORNADA (Total: {len(relevos)})")
print("=" * 90)
for r in relevos:
    print(f"  DNI: {r['DNI']} - {r['Nombre'].ljust(32)} | Turno: {r['Turno'].ljust(5)} | Horario: {r['Horario'].ljust(22)} | Obs: {r['Obs']}")

print("\n" + "=" * 90)
print(f"3. TURNOS NORMALES COMPLETOS (Total: {len(normales)})")
print("=" * 90)
for n in normales:
    print(f"  DNI: {n['DNI']} - {n['Nombre'].ljust(32)} | Turno: {n['Turno'].ljust(5)} | Horario: {n['Horario'].ljust(22)} | Tipo: {n['Tipo'].ljust(15)} | Obs: {n['Obs']}")
