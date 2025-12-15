# -------------------
# Script unificato per la creazione di heatmap
# -------------------
import csv, folium
from folium.plugins import HeatMap


def crea_heatmap(input_file, output_file, titolo="Heatmap"):
    """
    Crea una heatmap da un file CSV con dati di gravità.
    
    Args:
        input_file: Path del file CSV con colonne id, lat, lon, gravita
        output_file: Path del file HTML di output
        titolo: Titolo descrittivo per il messaggio di conferma
    """
    # Centro Parma
    centro_parma = [44.801485, 10.3279036]

    # Carica dati dal file e filtra punti validi
    dati = []
    with open(input_file, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)  # Salta intestazione
        for row in reader:
            try:
                lat = float(row[1])
                lon = float(row[2])
                gravita = float(row[3])
                if lat != 0 and lon != 0 and gravita != 0:
                    dati.append([lat, lon, gravita])
            except (ValueError, IndexError):
                continue

    # Crea la mappa
    mappa = folium.Map(location=centro_parma, zoom_start=14)
    HeatMap(dati, radius=40, blur=25, max_zoom=14).add_to(mappa)
    mappa.save(output_file)

    print(f"{titolo} salvata in '{output_file}' con {len(dati)} punti validi")


def crea_tutte_heatmap():
    """Crea tutte le heatmap della pipeline"""
    print("\n" + "="*60)
    print("CREAZIONE HEATMAP")
    print("="*60 + "\n")
    
    # Heatmap esperimento (articoli)
    print("1/2: Creazione heatmap da dati esperimento (articoli)...")
    crea_heatmap(
        input_file="5.Pipeline_Dataset/3.rischio_esperimento.csv",
        output_file="heatmap_esperimento.html",
        titolo="Heatmap esperimento"
    )
    
    # Heatmap OpenData
    print("\n2/2: Creazione heatmap da dati OpenData...")
    crea_heatmap(
        input_file="6. Mappa OpenData/3.rischio_opendata.csv",
        output_file="heatmap_opendata.html",
        titolo="Heatmap OpenData"
    )
    
    print("\n" + "="*60)
    print("✓ Tutte le heatmap create con successo!")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 3:
        # Uso: python crea_heatmap.py <input_file> <output_file>
        crea_heatmap(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "--esperimento":
        # Crea solo heatmap esperimento
        crea_heatmap(
            "5.Pipeline_Dataset/3.rischio_esperimento.csv",
            "heatmap_esperimento.html",
            "Heatmap esperimento"
        )
    elif len(sys.argv) > 1 and sys.argv[1] == "--opendata":
        # Crea solo heatmap OpenData
        crea_heatmap(
            "6. Mappa OpenData/3.rischio_opendata.csv",
            "heatmap_opendata.html",
            "Heatmap OpenData"
        )
    else:
        # Crea tutte le heatmap
        crea_tutte_heatmap()
