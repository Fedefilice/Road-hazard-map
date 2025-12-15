import pandas as pd
import csv

# Carica i dataset
benchmark_df = pd.read_csv("4. Script finale 899/dataset_etichettato_900.csv", sep=';', encoding='utf-8')
risultato_df = pd.read_csv("4. Script finale 899/prompt_900.csv", sep=';', encoding='utf-8')

# Lista delle etichette (nomi nel benchmark_df)
etichette_benchmark = ['localizzazione', 'tempo', 'grave', 'moto', 'deboli']
# Lista delle etichette (nomi nel risultato_df)
etichette_risultato = ['localizzazione', 'tempo', 'grave', 'moto', 'utenti_deboli']

# Output unico
output_path = "8.Miglioramento prompting/differenze.csv"

# Crea le intestazioni
header = ['frase']
for etichetta in etichette_benchmark:
    nome_display = 'utenti_deboli' if etichetta == 'deboli' else etichetta
    header.append(f'{nome_display}_benchmark')
    header.append(f'{nome_display}_risultato')

# Apri il file CSV in scrittura
with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(header)
    
    for idx in range(len(benchmark_df)):
        # estrai le frasi per verifica
        frase_bench = benchmark_df.iloc[idx]['frase']
        frase_ris = risultato_df.iloc[idx]['frase']
        # se non corrispondono, salta
        if frase_bench != frase_ris:
            print(f"Le frasi non corrispondono all'indice {idx}!")
            continue 
        
        # Verifica se ci sono differenze in almeno una etichetta
        ha_differenze = False
        for etich_bench, etich_ris in zip(etichette_benchmark, etichette_risultato):
            val_bench = benchmark_df.iloc[idx][etich_bench]
            val_ris = risultato_df.iloc[idx][etich_ris]
            if val_bench != val_ris:
                ha_differenze = True
                break
        
        # Se ci sono differenze, scrivi la riga
        if ha_differenze:
            row = [frase_bench]
            for etich_bench, etich_ris in zip(etichette_benchmark, etichette_risultato):
                row.append(benchmark_df.iloc[idx][etich_bench])
                row.append(risultato_df.iloc[idx][etich_ris])
            writer.writerow(row)

print(f"Script differenze completato")


