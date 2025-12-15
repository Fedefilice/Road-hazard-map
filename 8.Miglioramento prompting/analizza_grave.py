import pandas as pd

# Leggi il file
df = pd.read_csv('differenze.csv', sep=';')

print("="*100)
print("ANALISI ERRORI - GRAVE")
print("="*100)

# Errori grave
errori_grave = df[df['grave_benchmark'] != df['grave_risultato']]
print(f'\nErrori totali GRAVE: {len(errori_grave)}')

# Falsi positivi (0->1): Il modello identifica gravità quando NON c'è
falsi_positivi = errori_grave[(errori_grave['grave_benchmark']==0) & (errori_grave['grave_risultato']==1)]
print(f'Falsi positivi (0->1 - gravità rilevata erroneamente): {len(falsi_positivi)}')

# Falsi negativi (1->0): Il modello NON identifica gravità quando c'è
falsi_negativi = errori_grave[(errori_grave['grave_benchmark']==1) & (errori_grave['grave_risultato']==0)]
print(f'Falsi negativi (1->0 - gravità mancata): {len(falsi_negativi)}')

print("\n" + "="*100)
print("ANALISI FALSI POSITIVI - Gravità rilevata erroneamente")
print("="*100)
print(f"\nTotale falsi positivi: {len(falsi_positivi)}")
print("\nPrime 20 frasi dove il modello identifica gravità quando NON c'è:\n")
for idx, row in falsi_positivi.head(20).iterrows():
    print(f"Frase: {row['frase']}")
    print("-" * 100)

print("\n" + "="*100)
print("ANALISI FALSI NEGATIVI - Gravità mancata")
print("="*100)
print(f"\nTotale falsi negativi: {len(falsi_negativi)}")
print("\nPrime 20 frasi dove il modello NON identifica gravità quando c'è:\n")
for idx, row in falsi_negativi.head(20).iterrows():
    print(f"Frase: {row['frase']}")
    print("-" * 100)

# Analisi parole chiave nei falsi positivi
print("\n" + "="*100)
print("ANALISI PAROLE CHIAVE - FALSI POSITIVI")
print("="*100)

parole_sospette = {
    'ferite/feriti': [],
    'condizioni': [],
    'pronto soccorso/ospedale': [],
    'gravi (ma FP)': [],
    'media gravità': [],
    'soccorsi/118': [],
    'traumi': [],
    'ricoverato': []
}

for idx, row in falsi_positivi.iterrows():
    frase = row['frase'].lower()
    
    if 'ferit' in frase:
        parole_sospette['ferite/feriti'].append(row['frase'])
    if 'condizioni' in frase:
        parole_sospette['condizioni'].append(row['frase'])
    if 'pronto soccorso' in frase or 'ospedale' in frase:
        parole_sospette['pronto soccorso/ospedale'].append(row['frase'])
    if 'gravi' in frase or 'grave' in frase:
        parole_sospette['gravi (ma FP)'].append(row['frase'])
    if 'media gravità' in frase or 'media gravita' in frase:
        parole_sospette['media gravità'].append(row['frase'])
    if 'soccors' in frase or '118' in frase:
        parole_sospette['soccorsi/118'].append(row['frase'])
    if 'traum' in frase:
        parole_sospette['traumi'].append(row['frase'])
    if 'ricoverat' in frase:
        parole_sospette['ricoverato'].append(row['frase'])

for chiave, frasi in parole_sospette.items():
    print(f"\n{chiave.upper()}: {len(frasi)} occorrenze")
    if len(frasi) > 0:
        print("Esempi:")
        for i, frase in enumerate(frasi[:3], 1):
            print(f"  {i}. {frase[:150]}...")

# Analisi parole chiave nei falsi negativi
print("\n" + "="*100)
print("ANALISI PAROLE CHIAVE - FALSI NEGATIVI")
print("="*100)

parole_mancate = {
    'grave/gravi presente': [],
    'morto/deceduto': [],
    'prognosi riservata': [],
    'condizioni serie': [],
    'gravissimo': [],
    'pericolo di vita': []
}

for idx, row in falsi_negativi.iterrows():
    frase = row['frase'].lower()
    
    if 'grave' in frase or 'gravi' in frase:
        parole_mancate['grave/gravi presente'].append(row['frase'])
    if 'mort' in frase or 'decedut' in frase or 'vittima' in frase:
        parole_mancate['morto/deceduto'].append(row['frase'])
    if 'prognosi riservata' in frase:
        parole_mancate['prognosi riservata'].append(row['frase'])
    if 'condizioni serie' in frase or 'condizioni gravi' in frase:
        parole_mancate['condizioni serie'].append(row['frase'])
    if 'gravissim' in frase:
        parole_mancate['gravissimo'].append(row['frase'])
    if 'pericolo di vita' in frase:
        parole_mancate['pericolo di vita'].append(row['frase'])

for chiave, frasi in parole_mancate.items():
    print(f"\n{chiave.upper()}: {len(frasi)} occorrenze")
    if len(frasi) > 0:
        print("Esempi:")
        for i, frase in enumerate(frasi[:3], 1):
            print(f"  {i}. {frase[:150]}...")
