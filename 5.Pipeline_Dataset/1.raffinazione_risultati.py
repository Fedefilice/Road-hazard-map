import csv

input_file = "5.Pipeline_Dataset/output_articoli_frasi_corrected.csv"
output_file = "5.Pipeline_Dataset/1.articoli_OR.csv"

# Restituisce un file con le stesse colonne ma etichette modificate.
# Inserisce articoli in OR per non ripetere etichette a 1 per lo stesso articolo

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "w", newline="", encoding="utf-8") as f_out:
    reader = csv.DictReader(f_in, delimiter=';')
    writer = csv.writer(f_out, delimiter=';')
    writer.writerow(["articolo_id", "frase", "localizzazione", "grave"])

    last_id = None
    counter = [0]*5
    buffer = []
    grave_present = False        

    for row in reader:
        articolo_id = row['articolo_id']
        frase = row['articolo']
        etichette = [int(row['localizzazione']), int(row['tempo']), int(row['grave']), int(row['moto']), int(row['utenti_deboli'])]

        # Quando cambia articolo, processa il buffer
        if articolo_id != last_id and last_id is not None:
            # se almeno una frase ha grave=1, allora diventa True
            grave_in_articolo = any(row[3] == 1 for row in buffer) 
            for row in buffer: #itera su tutte le frasi dell'articolo
                if row[2] == 1: # se localizzazione=1, mantieni la frase
                    if grave_in_articolo: # se grave presente, imposta grave=1
                        row[3] = 1
                    writer.writerow(row) # scrivi in output csv
                    break
            buffer.clear()

        last_id = articolo_id # aggiorna l'ID articolo corrente
        buffer.append([articolo_id, frase, etichette[0], etichette[2]])

    # Flush dell'ultimo articolo
    if buffer:
            grave_in_articolo = any(row[3] == 1 for row in buffer) 
            for row in buffer: 
                if row[2] == 1:
                    if grave_in_articolo:
                        row[3] = 1
                    writer.writerow(row) 
                    break
            buffer.clear()
print(f"Termine esecuzione OR per articolo.")