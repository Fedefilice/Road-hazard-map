# -------------------
# Calcolo gravità - Dataset esperimento (articoli di giornale)
# -------------------
import sys

sys.path.insert(0, ".")

from calcola_gravita import calcola_griglia_gravita
from crea_heatmap import crea_heatmap

if __name__ == "__main__":
    input_file = "5.Pipeline_Dataset/2.articoli_geolocalizzati.csv"
    output_file = "5.Pipeline_Dataset/3.rischio_esperimento.csv"
    output_heatmap = "heatmap_esperimento.html"
    
    # Calcola gravità
    calcola_griglia_gravita(input_file, output_file)
    
    # Crea heatmap
    print("\nCreazione heatmap...")
    crea_heatmap(output_file, output_heatmap, "Heatmap esperimento")