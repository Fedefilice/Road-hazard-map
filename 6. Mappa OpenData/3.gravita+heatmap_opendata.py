# -------------------
# Calcolo gravità - Dataset OpenData ufficiale
# -------------------
import sys

sys.path.insert(0, ".")

from calcola_gravita import calcola_griglia_gravita
from crea_heatmap import crea_heatmap


if __name__ == "__main__":
    input_file = "6. Mappa OpenData/incidenti_ripuliti.csv"
    output_file = "6. Mappa OpenData/3.rischio_opendata.csv"
    output_heatmap = "heatmap_opendata.html"
    
    # Calcola gravità
    calcola_griglia_gravita(input_file, output_file)
    
    # Crea heatmap
    print("\nCreazione heatmap...")
    crea_heatmap(output_file, output_heatmap, "Heatmap OpenData")