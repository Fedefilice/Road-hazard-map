# -------------------
# Script calcolo gravità e gestione outlier 
# -------------------
import csv, statistics, math
import numpy as np
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic

# -------------------
# PARAMETRI
# -------------------
SIDE = 0.5
PASSO = 0.5
SIGMA = 500  

''' Creazione del poligono del comune di Parma per scremare nel comune di Parma,
    funzione per il calcolo della gravità,
    gestione outlier e scrittura su file CSV.
'''

# Poligono del comune di Parma
# selezionato manualmente dalla cartina comunale
# https://mappe.comune.parma.it/mokaApp/apps/STRWEB_H5/index.html
PARMA_POLYGON = Polygon([
    (10.232051, 44.774007),
    (10.278829, 44.764799),
    (10.235895, 44.719063),
    (10.296174, 44.703151),
    (10.292636, 44.67175),
    (10.30943, 44.661555),
    (10.331891, 44.680469),
    (10.341226, 44.716088),
    (10.374666, 44.703424),
    (10.389603, 44.741472),
    (10.426882, 44.742084),
    (10.432284, 44.751068),
    (10.426423, 44.798123),
    (10.439263, 44.799927),
    (10.446011, 44.818956),
    (10.415668, 44.833687),
    (10.417185, 44.8819),
    (10.361398, 44.874481),
    (10.298083, 44.889152),
    (10.291177, 44.902449),
    (10.268553, 44.87948),
    (10.237834, 44.876363),
    (10.213722, 44.804929),
    (10.242442, 44.798547),
    (10.232314, 44.7746),
])

# Verifica se un punto è all'interno del poligono di Parma
def is_within_parma(lat, lon):
    try:
        point = Point(float(lon), float(lat))
        return point.within(PARMA_POLYGON)
    except Exception:
        print(f"Errore nel controllo delle coordinate.")
        return False

# creazione bounding box attorno a un punto centrale
def bbox(center_lat, center_lon):
    half_side = SIDE / 2
    north = geodesic(half_side).destination((center_lat, center_lon), 0)
    south = geodesic(half_side).destination((center_lat, center_lon), 180)
    east  = geodesic(half_side).destination((center_lat, center_lon), 90)
    west  = geodesic(half_side).destination((center_lat, center_lon), 270)
    return (south.latitude, west.longitude, north.latitude, east.longitude)

# Genera una griglia di punti all'interno del poligono di Parma
def punti_nel_poligono_griglia(passo=PASSO):
    punti = []
    minx, miny, maxx, maxy = PARMA_POLYGON.bounds
    lat_corrente = miny
    while lat_corrente <= maxy:
        lon_corrente = minx
        while lon_corrente <= maxx:
            if is_within_parma(lat_corrente, lon_corrente):
                punti.append((lat_corrente, lon_corrente))
            est = geodesic(passo).destination((lat_corrente, lon_corrente), 90)
            lon_corrente = est.longitude
        nord = geodesic(passo).destination((lat_corrente, minx), 0)
        lat_corrente = nord.latitude
    return punti

# calcola gravità su griglia in base agli incidenti all'interno della bounding box
# output su file CSV
def calcola_griglia_gravita(input_file, output_file):
    # Leggi header e trova indici colonne
    with open(input_file, "r", encoding="utf-8") as f_in:
        reader = csv.reader(f_in, delimiter=';')
        header = next(reader)
        
        idx_grave = header.index("grave")
        idx_lat = header.index("latitudine")
        idx_lon = header.index("longitudine")

    # Leggi incidenti
    incidenti = []
    with open(input_file, "r", encoding="utf-8") as f_in:
        reader = csv.reader(f_in, delimiter=';')
        next(reader)  # skip header
        for row in reader:
            try:
                lat_inc = float(row[idx_lat])
                lon_inc = float(row[idx_lon])
                grave = float(row[idx_grave])
                incidenti.append((lat_inc, lon_inc, grave))
            except (ValueError, IndexError):
                continue
    
    # Conta incidenti dentro il poligono del comune di Parma
    incidenti_nel_poligono = sum(1 for lat, lon, _ in incidenti if is_within_parma(lat, lon))
    
    print(f"Incidenti totali: {len(incidenti)}")
    print(f"Incidenti nel comune di Parma: {incidenti_nel_poligono}")
    
    # Genera griglia
    lista_punti = punti_nel_poligono_griglia()
    punti_griglia = []
    gravita_vals = []
    counter = 0

    # -------------------
    # Calcolo gravità solo per punti nel comune di Parma
    # -------------------
    for lat_p, lon_p in lista_punti:
        if is_within_parma(lat_p, lon_p):
            lat_s, lon_w, lat_n, lon_e = bbox(lat_p, lon_p)
            gravita = 0
            counter += 1
            
            for lat_inc, lon_inc, grave in incidenti:
                if lat_s <= lat_inc <= lat_n and lon_w <= lon_inc <= lon_e:
                    #dist = geodesic((lat_p, lon_p), (lat_inc, lon_inc)).meters
                    weight = 1.0 if grave == 1.0 else 0.5
                    gravita += weight #* math.exp(- (dist ** 2) / (2 * (SIGMA ** 2)))
            
            punti_griglia.append([counter, lat_p, lon_p, gravita])
            gravita_vals.append(gravita)

    # -------------------
    # Gestione outlier e calcolo statistiche
    # -------------------
    gravita_nonzero = [v for v in gravita_vals if v > 0]
    
    if gravita_nonzero:
        # calcolo statistiche base
        media = statistics.mean(gravita_nonzero)
        dev_std = statistics.stdev(gravita_nonzero) if len(gravita_nonzero) > 1 else 0.0
        
        print(f"\nStatistiche gravità (solo >0):")
        print(f"  Max: {max(gravita_nonzero):.4f}")
        print(f"  Media: {media:.4f}")
        print(f"  Deviazione standard: {dev_std:.4f}\n")

        # Gestione outlier con metodo IQR 
        gravita_array = np.array(gravita_nonzero)
        
        # Calcola quartili usando numpy.percentile
        q1 = np.percentile(gravita_array, 25)
        q2 = np.percentile(gravita_array, 50)
        q3 = np.percentile(gravita_array, 75)
        iqr = q3 - q1
        
        # Soglia outlier (usando k=3 invece di 1.5)
        k = 3.0
        soglia_outlier = q3 + k * iqr
        
        print(f"Metodo IQR (Tukey) con k={k}:")
        print(f"  Q1 (primo quartile): {q1:.4f}")
        print(f"  Q2 (mediana): {q2:.4f}")
        print(f"  Q3 (terzo quartile): {q3:.4f}")
        print(f"  IQR (Q3 - Q1): {iqr:.4f}")
        print(f"  Soglia outlier (Q3 + {k}*IQR): {soglia_outlier:.4f}")
        
        num_outlier = sum(1 for row in punti_griglia if row[3] > soglia_outlier)
        print(f"Outlier trovati e tagliati: {num_outlier}")
        
        for row in punti_griglia:
            if row[3] > soglia_outlier:
                row[3] = soglia_outlier

        # Scrivi output
        with open(output_file, "w", encoding="utf-8", newline="") as f_out:
            writer = csv.writer(f_out, delimiter=';')
            writer.writerow(["id", "lat", "lon", "gravita"])
            for row in punti_griglia:
                writer.writerow([row[0], row[1], row[2], round(row[3], 4)])
        
        print(f"File '{output_file}' creato con {len(punti_griglia)} punti.")
    else:
        print("Nessun punto con gravità > 0 trovato.")


if __name__ == "__main__":
    # Esempio di utilizzo diretto
    import sys
    if len(sys.argv) == 3:
        calcola_griglia_gravita(sys.argv[1], sys.argv[2])
    else:
        print("Uso: python calcola_gravita_comune.py <input_file> <output_file>")
        print("Il file di input deve avere le colonne: grave, latitudine, longitudine")
