import csv

'''Normalizzazione Min-Max dei valori di gravità calcolata e opendata.
   I valori vengono normalizzati dividendo per il massimo del rispettivo dataset.
   Viene calcolata anche la media e la differenza tra i due valori normalizzati.
'''

# File di input
file_input = "7.Analisi dati/1.unione_gravita.csv"
output_file_normalizzato = "7.Analisi dati/3.normalizzazione_minmax.csv"


def leggi_unione_gravita(file_path):
    coords_dict = {}
    max_calc = 0
    max_open = 0
    
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            lat = float(row["latitudine"])
            lon = float(row["longitudine"])
            grav_calc = float(row["gravita_calcolata"])
            grav_open = float(row["gravita_opendata"])
            
            coords_dict[(lat, lon)] = (grav_calc, grav_open)
            max_calc = max(max_calc, grav_calc)
            max_open = max(max_open, grav_open)
    
    return coords_dict, max_calc, max_open


def salva_csv_normalizzato(coords_dict, max_calc, max_open, output_path):
    with open(output_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out, delimiter=';')
        writer.writerow(["latitudine", "longitudine", "gravita_calcolata", 
                        "gravita_opendata", "media", "differenza"])
        
        for (lat, lon), (grav_calc, grav_open) in sorted(coords_dict.items()):
            # Normalizza dividendo per il massimo del rispettivo dataset
            grav_calc_norm = grav_calc / max_calc
            grav_open_norm = grav_open / max_open
            media = (grav_calc_norm + grav_open_norm) / 2
            differenza = grav_open_norm - grav_calc_norm
            writer.writerow([lat, lon, round(grav_calc_norm, 3), round(grav_open_norm, 3), 
                           round(media, 3), round(differenza, 3)])


def main():
    # Leggi i dati
    coords_dict, max_calc, max_open = leggi_unione_gravita(file_input)
    
    # Normalizzazione Min-Max (divisione per massimo)
    print("\n=== NORMALIZZAZIONE MIN-MAX ===")
    print(f"Massimo gravità calcolata: {max_calc}")
    print(f"Massimo gravità opendata: {max_open}")
    
    salva_csv_normalizzato(coords_dict, max_calc, max_open, output_file_normalizzato)
    print(f"File salvato: {output_file_normalizzato}")


if __name__ == "__main__":
    main()