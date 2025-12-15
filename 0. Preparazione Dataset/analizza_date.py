import re

# Analizza file vecchio
file_vecchio = r'c:\Users\feder\OneDrive\Desktop\Tirocinio\Testing\0. Preparazione Dataset\articoli_parma.txt'
with open(file_vecchio, 'r', encoding='latin-1') as f:
    content = f.read()

dates = re.findall(r'~ (\d{1,2} (?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre) \d{4})', content)
years = [int(d.split()[-1]) for d in dates]

print(f'FILE VECCHIO:')
print(f'  Articoli totali: {len(dates)}')
if years:
    print(f'  Anno più vecchio: {min(years)}')
    print(f'  Anno più recente: {max(years)}')
    year_counts = {}
    for y in years:
        year_counts[y] = year_counts.get(y, 0) + 1
    print('  Distribuzione per anno:')
    for year, count in sorted(year_counts.items()):
        print(f'    {year}: {count} articoli')

# Analizza file nuovo (se esistente)
file_nuovo = r'c:\Users\feder\OneDrive\Desktop\Tirocinio\Testing\articoli_parma.txt'
try:
    with open(file_nuovo, 'r', encoding='utf-8') as f:
        content_nuovo = f.read()
    
    dates_nuovo = re.findall(r'~ (\d{1,2} (?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre) \d{4})', content_nuovo)
    years_nuovo = [int(d.split()[-1]) for d in dates_nuovo]
    
    print(f'\nFILE NUOVO:')
    print(f'  Articoli totali: {len(dates_nuovo)}')
    if years_nuovo:
        print(f'  Anno più vecchio: {min(years_nuovo)}')
        print(f'  Anno più recente: {max(years_nuovo)}')
        year_counts_nuovo = {}
        for y in years_nuovo:
            year_counts_nuovo[y] = year_counts_nuovo.get(y, 0) + 1
        print('  Distribuzione per anno:')
        for year, count in sorted(year_counts_nuovo.items()):
            print(f'    {year}: {count} articoli')
except FileNotFoundError:
    print(f'\nFILE NUOVO: Non ancora creato o incompleto')
