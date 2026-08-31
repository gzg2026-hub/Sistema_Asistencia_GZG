import pandas as pd
raw = pd.read_excel('downloads/data_cruda/Transacciones_Acumuladas.xlsx')
dnis = ['60876523', '62772089', '72500789', '72909375', '72940901', '73485498']

print("=" * 80)
print("HISTORIAL DE MARCACIONES CRUDAS (27 AL 31 DE AGOSTO)")
print("=" * 80)

for dni in dnis:
    dni_norm = str(dni).zfill(8)
    sub = raw[raw['ID'].astype(str).str.zfill(8) == dni_norm]
    sub = sub[sub['Fecha'] >= '2026-08-27'].sort_values(['Fecha', 'Tiempo'])
    nombre = f"{sub.iloc[0]['Apellido']} {sub.iloc[0]['Nombre']}" if not sub.empty else 'Desconocido'
    print(f"\nDNI: {dni_norm} | {nombre}")
    print("-" * 75)
    for _, r in sub.iterrows():
        f = str(r.get('Fecha', ''))
        t = str(r.get('Tiempo', ''))
        tp = str(r.get('Tipo de pase de tarjeta', ''))
        print(f"  {f} | {t} | {tp}")
