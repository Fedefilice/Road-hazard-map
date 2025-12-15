import csv

# File paths
dataset_file = "0. Preparazione Dataset/dataset_articoli_frasi.csv"
output_file = "5.Pipeline_Dataset/output_articoli_frasi.csv"
corrected_file = "5.Pipeline_Dataset/output_articoli_frasi_corrected.csv"

# Leggi il dataset di riferimento e crea un dizionario: indice riga -> (articolo_id, articolo)
riga_to_data = {}
with open(dataset_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for idx, row in enumerate(reader):
        riga_to_data[idx] = {
            'articolo_id': row['articolo_id'],
            'articolo': row['articolo']
        }

print(f"Caricate {len(riga_to_data)} righe dal dataset di riferimento")

# Leggi il file output e correggi SOLO gli ID, mantenendo tutte le altre colonne invariate
with open(output_file, 'r', encoding='utf-8') as f_in, \
     open(corrected_file, 'w', newline='', encoding='utf-8') as f_out:
    
    reader = csv.DictReader(f_in, delimiter=';')
    
    # Scrivi l'header con le 7 colonne corrette
    fieldnames = ['articolo_id', 'articolo', 'localizzazione', 'tempo', 'grave', 'moto', 'utenti_deboli']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    
    # Leggi il resto del file e sovrascrivi con i dati dal dataset di riferimento
    for idx, row in enumerate(reader):
        # Usa i dati dal dataset di riferimento (sia articolo_id che articolo)
        if idx in riga_to_data:
            row_data = {
                'articolo_id': riga_to_data[idx]['articolo_id'],
                'articolo': riga_to_data[idx]['articolo'],
                'localizzazione': row['localizzazione'],
                'tempo': row['tempo'],
                'grave': row['grave'],
                'moto': row['moto'],
                'utenti_deboli': row['utenti_deboli']
            }
        else:
            # Se per qualche motivo l'indice non esiste, mantieni i dati originali
            row_data = {
                'articolo_id': row['articolo_id'],
                'articolo': row['articolo'],
                'localizzazione': row['localizzazione'],
                'tempo': row['tempo'],
                'grave': row['grave'],
                'moto': row['moto'],
                'utenti_deboli': row['utenti_deboli']
            }
        
        writer.writerow(row_data)

print(f"\nCorrezione completata!")
print(f"File salvato in: {corrected_file}")
