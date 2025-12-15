import csv

input_file = "dataset_etichettato_900.csv"
output_file = "dataset_ridotto_200.csv"

# Leggi il file CSV originale e prendi solo le prime 200 righe
with open(input_file, "r", encoding="utf-8") as f_input, \
     open(output_file, "w", newline="", encoding="utf-8") as f_output:
    
    reader = csv.reader(f_input, delimiter=';')
    writer = csv.writer(f_output, delimiter=';')
    
    # Copia le prime 200 righe (incluso l'header)
    for i, row in enumerate(reader):
        if i < 200:
            writer.writerow(row)
        else:
            break