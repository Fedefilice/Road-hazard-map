import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

'''Crea grafici di distribuzione affiancati per due dataset,
   calcolando IQR e mediana.
'''

def crea_grafici_distribuzione(df_opendata, df_calcolata, titolo_suptitle, bin_width=0.5):
    # Calcola IQR per entrambi i dataset
    q1_op, q3_op = np.percentile(df_opendata, [25, 75])
    q1_calc, q3_calc = np.percentile(df_calcolata, [25, 75])
    iqr_op = q3_op - q1_op
    iqr_calc = q3_calc - q1_calc
    
    # Calcola bins con range specificato
    bins_opendata = int((df_opendata.max() - df_opendata.min()) / bin_width) + 1
    bins_calcolata = int((df_calcolata.max() - df_calcolata.min()) / bin_width) + 1
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Istogramma OpenData con frequenze relative percentuali
    n1, _, _ = ax1.hist(df_opendata, bins=bins_opendata, color='steelblue', edgecolor='black', alpha=0.7,
                        weights=np.ones(len(df_opendata)) / len(df_opendata) * 100)
    ax1.set_xlabel('Rischio incidenti OpenData')
    ax1.set_ylabel('Frequenza relativa (%)')
    ax1.set_title(f'OpenData\n(n={len(df_opendata)}, IQR={iqr_op:.1f}, Mediana={df_opendata.median():.1f})')
    ax1.grid(True, alpha=0.3)
    
    # Istogramma Esperimento con frequenze relative percentuali
    n2, _, _ = ax2.hist(df_calcolata, bins=bins_calcolata, color='coral', edgecolor='black', alpha=0.7,
                        weights=np.ones(len(df_calcolata)) / len(df_calcolata) * 100)
    ax2.set_xlabel('Rischio incidenti calcolato')
    ax2.set_ylabel('Frequenza relativa (%)')
    ax2.set_title(f'Estratta dalle informazioni testuali\n(n={len(df_calcolata)}, IQR={iqr_calc:.1f}, Mediana={df_calcolata.median():.1f})')
    ax2.grid(True, alpha=0.3)
    
    # Sincronizza le scale con margini
    max_x_with_margin = max(df_opendata.max(), df_calcolata.max()) * 1.05
    max_y_with_margin = max(n1.max(), n2.max()) * 1.05
    
    ax1.set_xlim(0, max_x_with_margin)
    ax2.set_xlim(0, max_x_with_margin)
    ax1.set_ylim(0, max_y_with_margin)
    ax2.set_ylim(0, max_y_with_margin)
    
    plt.suptitle(titolo_suptitle, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

df = pd.read_csv("7.Analisi dati/1.unione_gravita.csv", delimiter=';')

# Filtra i dati escludendo gravità = 0
df_opendata = df[df['gravita_opendata'] != 0]['gravita_opendata']
df_calcolata = df[df['gravita_calcolata'] != 0]['gravita_calcolata']

crea_grafici_distribuzione(
    df_opendata,
    df_calcolata,
    'Istogramma dell\'indice di rischio stradale'
)