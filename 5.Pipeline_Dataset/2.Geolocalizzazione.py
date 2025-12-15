import spacy, csv, re, requests

# Prefissi: strada, piazza, piazzale
# Parole filtrate: ospedale, parma

nlp = spacy.load("it_nerIta_trf")

# Funzioni Nominatim
def get_coordinates(query):
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'MyGeocoder'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        osm_results = r.json()
        if osm_results:
            lat = float(osm_results[0].get("lat", 0))
            lon = float(osm_results[0].get("lon", 0))
            pos = osm_results[0].get("display_name", "Località sconosciuta")
            return lat, lon, pos
        else:
            print(f"Nessun risultato trovato per {query}")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta per {query}: {e}")
        return None, None, None

def estrai_coordinate_nominatim(entities_str):
    if entities_str:
        # inserisci in lista le entità divise (entità separate da virgola)
        entities = [e.strip() for e in entities_str.split(",") if e.strip()]
        if not entities: # error handling: lista vuota
            return None, None, None
        # Prova ogni entità singolarmente
        for ent in entities:
            # inserisci prefissi costanti per migliorare accuratezza
            single_query = f"{ent}, Parma, Emilia-Romagna, Italia"
            # chiama la HTTP GET request
            lat, lon, pos = get_coordinates(single_query)
            if lat and lon: # se coordinate valide, output
                return lat, lon, pos
        # Se nessuna singola funziona, prova tutte insieme
        combined_query = f"{', '.join(entities)}, Parma, Emilia-Romagna, Italia"
        lat, lon, pos = get_coordinates(combined_query)
        if lat and lon: # controllo se le coordinate sono valide
            return lat, lon, pos
    return None, None, None


# Estrazione NER
def estrai_luoghi_NER(doc, frase):
    entities = [] #lista di entità trovate
    seen = set()  #set per evitare duplicati
    for ent in doc.ents:
        # per le entità GPE e FAC trovate esclendo 'ospedale'
        if (ent.label_ == "GPE" or ent.label_ == "FAC") and "ospedale" not in ent.text.lower(): 
            # cerca prefissi nella frase
            pattern = re.compile(rf"(strada|piazza|piazzale)\s+{re.escape(ent.text)}", re.IGNORECASE) 
            if pattern.search(frase): # concatena prefisso + entità interessata
                match = pattern.search(frase)
                prefisso = match.group(1)
                entity = f"{prefisso} {ent.text}"
            else:
                entity = ent.text
            if entity not in seen: # evita duplicati
                entities.append(entity)
                seen.add(entity)
    # Rimuovi tutte le occorrenze di 'Parma'
    entities = [e for e in entities if not re.fullmatch(r"\s*parma\s*", e, re.IGNORECASE)]
    return entities


# Main
with open("5.Pipeline_Dataset/1.articoli_OR.csv", "r", encoding="utf-8") as f_in, \
     open("5.Pipeline_Dataset/2.articoli_geolocalizzati.csv", "w", encoding="utf-8", newline="") as f_out:
    reader = csv.reader(f_in, delimiter=';')
    header = next(reader)
    id = header.index("articolo_id")
    frase = header.index("frase")
    localizzazione = header.index("localizzazione")
    grave = header.index("grave")


    writer = csv.writer(f_out, delimiter=";")
    writer.writerow(["articolo_id", "frase", "entities", "grave", "latitudine", "longitudine", "pos"])


    for row in reader:
        r_articolo_id = row[id]
        r_frase = row[frase]
        r_localizzazione = row[localizzazione]
        r_grave = row[grave]

        doc = nlp(r_frase)
        entities = estrai_luoghi_NER(doc, r_frase) # estrazione NER
        entities_str = ", ".join(entities)
        
        lat, lon, pos = estrai_coordinate_nominatim(entities_str) # estrazione Nominatim
        if lat is not None and lon is not None:
            writer.writerow([
                r_articolo_id,
                r_frase,
                entities_str,
                r_grave,
                lat,
                lon,
                pos if pos else ""
            ])

print("Termine geolocalizzazione con NER e Nominatim.")