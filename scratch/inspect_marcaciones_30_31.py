import pandas as pd
raw = pd.read_excel('downloads/data_cruda/Transacciones_Acumuladas.xlsx')
dnis = ['60876523', '62772089', '72500789', '72909375', '72940901', '73485498']

print("=" * 80)
print("MARCACIONES CRUDAS REGISTRADAS EN BIOMÉTRICO (30 Y 31 DE AGOSTO)")
print("=" * 80)

for dni in dnis:
    dni_norm = str(dni).zfill(8)
    sub = raw[raw['ID'].astype(str).str.zfill(8) == dni_norm]
    sub = sub[sub['Fecha'].isin(['2026-08-30', '2026-08-31'])].sort_values(['Fecha', 'Tiempo'])
    nombre = f"{sub.iloc[0]['Apellido']} {sub.iloc[0]['Nombre']}" if not sub.empty else 'Desconocido'
    print(f"\nDNI: {dni_norm} | {nombre}")
    print("-" * 75)
    for _, r in sub.iterrows():
        f = str(r.get('Fecha', ''))
        t = str(r.get('Tiempo', ''))
        tp = str(r.get('Tipo de pase de tarjeta', ''))
        mv = str(r.get('Método de verificación', ''))
        pc = str(r.get('Punto de control de asistencia', ''))
        print(f"  {f} | {t} | {tp.ljust(24)} | {mv.ljust(18)} | {pc}")

print("\n" + "=" * 80)
print("EVALUACIÓN EN EL REPORTE PROCESADO (30 DE AGOSTO)")
print("=" * 80)
rep = pd.read_excel('downloads/data_procesada/diario/Reporte_Asistencia_GZG_2026-08-30.xlsx', header=3)
sub_rep = rep[rep['DNI'].astype(str).str.zfill(8).isin([str(d).zfill(8) for d in dnis])]
for _, r in sub_rep.iterrows():
    dni_r = str(r.get('DNI', '')).zfill(8)
    ap = str(r.get('Apellidos', ''))
    nom = str(r.get('Nombres', ''))
    turno = str(r.get('Turno', ''))
    f_ent = str(r.get('Fecha Entrada', ''))
    h_ent = str(r.get('Hora Entrada', ''))
    f_sal = str(r.get('Fecha Salida', ''))
    h_sal = str(r.get('Hora Salida', ''))
    hrs = str(r.get('Horas de Turno', ''))
    reg = str(r.get('Tipo Registro', ''))
    obs = str(r.get('Observación / Incidencias', ''))
    print(f"{dni_r} | {ap} {nom} | Turno: {turno.ljust(5)} | {f_ent} {h_ent} -> {f_sal} {h_sal} | Hrs: {hrs} | Reg: {reg} | Obs: {obs}")
