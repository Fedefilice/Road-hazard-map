import csv

''' Script per unire i dataset di gravità calcolata e OpenData
    in un unico file CSV con le seguenti colonne:
- latitudine
- longitudine
- gravita_calcolata
- gravita_opendata
- media
- differenza
'''

# File di input
file_calcolata = "5.Pipeline_Dataset/3.rischio_esperimento.csv"  # gravità_calcolata
file_opendata = "6. Mappa OpenData/3.rischio_opendata.csv"        # gravità_opendata
output_file = "7.Analisi dati/1.unione_gravita.csv"


def carica_gravita(file_path, col_lat="lat", col_lon="lon", col_grav="gravita"):
    """Carica i dati di gravità in un dizionario {(lat, lon): gravità}"""
    gravita_dict = {}
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            lat = float(row[col_lat])
            lon = float(row[col_lon])
            gravita = float(row[col_grav])
            gravita_dict[(lat, lon)] = gravita
    return gravita_dict


# Carica entrambi i dataset
opendata_dict = carica_gravita(file_opendata)
calcolata_dict = carica_gravita(file_calcolata)

# Scrivi il file di output unificato
with open(output_file, "w", encoding="utf-8", newline="") as f_out:
    writer = csv.writer(f_out, delimiter=';')
    writer.writerow(["latitudine", "longitudine", "gravita_calcolata", "gravita_opendata", "media", "differenza"])
    
    for (lat, lon), grav_opendata in opendata_dict.items():
        grav_calc = calcolata_dict.get((lat, lon), 0.0)
        media = (grav_opendata + grav_calc) / 2
        differenza = grav_opendata - grav_calc
        writer.writerow([lat, lon, grav_calc, grav_opendata, round(media, 6), round(differenza, 6)])

print(f"Punti incrociati e scritti: {len(opendata_dict)}")