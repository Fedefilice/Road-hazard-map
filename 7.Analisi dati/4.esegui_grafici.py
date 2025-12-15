# -------------------
# Analisi grafici - Dataset unione gravità
# -------------------
import sys, subprocess

sys.path.insert(0, ".")

from grafici import analisi_grafici_confronto

if __name__ == "__main__":    
    # Analisi dati non bilanciati
    #analisi_grafici_confronto("7.Analisi dati/1.unione_gravita.csv")

    # 1. Calcolo gravità   esperimentos
    print("1/5: Calcolo gravità esperimento...")
    subprocess.run([sys.executable, "5.Pipeline_Dataset/3.gravita+heatmap_esperimento.py"], check=True)
    
    # 2. Calcolo gravità OpenData
    print("\n2/5: Calcolo gravità OpenData...")
    subprocess.run([sys.executable, "6. Mappa OpenData/3.gravita+heatmap_opendata.py"], check=True)
    
    # 3. Unione gravità
    print("\n3/5: Unione gravità...")
    subprocess.run([sys.executable, "7.Analisi dati/1.unione_gravita.py"], check=True)
    
    # 4. Normalizzazione
    print("\n4/5: Normalizzazione Min-Max...")
    subprocess.run([sys.executable, "7.Analisi dati/3.gestione_sbilanciamento.py"], check=True)
    
    
    # Analisi dati con normalizzazione min-max
    analisi_grafici_confronto("7.Analisi dati/3.normalizzazione_minmax.csv",)