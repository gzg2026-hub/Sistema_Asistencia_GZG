import pandas as pd
raw = pd.read_excel('downloads/data_cruda/Transacciones_Acumuladas.xlsx')
raw['DNI_NORM'] = raw['ID'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).apply(lambda d: str(d).lstrip('0').zfill(8))
sub = raw[raw['Fecha'] == '2026-08-30'].sort_values(['DNI_NORM', 'Tiempo'])

print(f"{'DNI':<10} | {'TRABAJADOR':<30} | {'TODAS LAS MARCACIONES DEL 30/08'}")
print("-" * 90)
for dni, g in sub.groupby('DNI_NORM'):
    swipes = [f"{r['Tiempo']} ({r['Tipo de pase de tarjeta']})" for _, r in g.iterrows()]
    nombre = f"{g.iloc[0]['Apellido']} {g.iloc[0]['Nombre']}"
    print(f"{dni:<10} | {nombre:<30} | {' | '.join(swipes)}")
