import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import os
import folium
from folium.plugins import HeatMap


def crea_grafici_analisi(df, col1, col2, titolo_col1, titolo_col2, titolo_generale):
    """
    Funzione riutilizzabile per creare i grafici di analisi (scatter + Bland-Altman)
    
    Parameters:
    -----------
    df : DataFrame con i dati da analizzare
    col1 : nome colonna per gravità calcolata
    col2 : nome colonna per gravità opendata
    titolo_col1 : titolo per l'asse Y
    titolo_col2 : titolo per l'asse X
    titolo_generale : titolo del grafico
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # --- Grafico 1: Pearson correlation ---
    ax1.scatter(df[col2], df[col1], alpha=0.5, color='deepskyblue')

    # Calcolo Pearson r 
    r_pearson, p_pearson = pearsonr(df[col2], df[col1])
    
    # Retta ideale y = x
    min_val = min(df[col2].min(), df[col1].min())
    max_val = max(df[col2].max(), df[col1].max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r-', label='y = x (corrispondenza perfetta)', linewidth=2)
    
    # Aggiungi Pearson nella leggenda
    if p_pearson < 0.05:
        pearson_label = f'Pearson r = {r_pearson:.2f}, p < 0.05'
    else:
        pearson_label = f'Pearson r = {r_pearson:.2f}, p = {p_pearson:.2f}'
    ax1.plot([], [], ' ', label=pearson_label)  # Elemento invisibile per aggiungere alla leggenda
    
    ax1.set_xlabel(titolo_col2, fontsize=15)
    ax1.set_ylabel(titolo_col1, fontsize=15)
    ax1.set_title(f'Scatter plot', fontsize=15)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')

    # --- Grafico 2: Bland-Altman ---
    mean_diff = df['differenza'].mean()
    std_diff = df['differenza'].std()
    loa_upper = mean_diff + 1.96 * std_diff
    loa_lower = mean_diff - 1.96 * std_diff

    ax2.scatter(df['media'], df['differenza'], alpha=0.5, color='steelblue', s=20)
    ax2.axhline(mean_diff, color="red", linestyle='-', linewidth=2, label=f'Bias: {mean_diff:.2f}')
    ax2.axhline(loa_upper, color="orange", linestyle='-', linewidth=1.5, label=f'LOA sup.: {loa_upper:.2f}')
    ax2.axhline(loa_lower, color="orange", linestyle='-', linewidth=1.5, label=f'LOA inf.: {loa_lower:.2f}')
    ax2.axhline(0, color='black', linestyle='-', linewidth=0.5, alpha=0.3)

    ax2.set_xlabel(f'Media: [(Riferimento + Sperimentale) / 2]', fontsize=15)
    ax2.set_ylabel(f'Differenza [Riferimento - Sperimentale]', fontsize=15)
    ax2.set_title(f'Bland-Altman Plot', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.suptitle(titolo_generale, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # Statistiche
    inside_loa = df[(df['differenza'] <= loa_upper) & (df['differenza'] >= loa_lower)]
    outside_loa = df[(df['differenza'] > loa_upper) | (df['differenza'] < loa_lower)]
    print(f"Limiti di accordo (95%):")
    print(f"  Superiore: {loa_upper:.4f}")
    print(f"  Inferiore: {loa_lower:.4f}")
    print(f"Punti dentro i limiti: {len(inside_loa)} ({len(inside_loa)/len(df)*100:.1f}%)")
    print(f"Punti fuori dai limiti: {len(outside_loa)} ({len(outside_loa)/len(df)*100:.1f}%)\n")


def analisi_grafici_confronto(input_file):
    titolo_col1="Indice pericolosità sperimentale"
    titolo_col2="Indice pericolosità riferimento"
    
    # Estrai il nome del file senza percorso
    nome_file = os.path.basename(input_file)
     
    df = pd.read_csv(input_file, delimiter=';')
    
    # Colonne fisse per tutti i file
    col1 = "gravita_calcolata"
    col2 = "gravita_opendata"

    # ============================================
    # PRIMO SET DI GRAFICI: CON punti dove entrambe gravità = 0
    # ============================================

    print("---------------------------")
    print("ANALISI CON PUNTI DOVE ENTRAMBE GRAVITÀ = 0")
    print(f"Punti totali: {len(df)}\n")

    crea_grafici_analisi(df, col1, col2, titolo_col1, titolo_col2, 
                         f'Analisi con tutti i punti (n={len(df)})')

    # ============================================
    # SECONDO SET DI GRAFICI: SENZA punti dove entrambe gravità = 0
    # ============================================

    # Filtra i punti dove entrambe le gravità sono 0
    df_filtered = df[~((df[col2] == 0) & (df[col1] == 0))]

    print("-----------------------")
    print("ANALISI SENZA PUNTI DOVE ENTRAMBE GRAVITÀ = 0")
    print(f"Punti totali: {len(df)}")
    print(f"Punti esclusi (entrambe gravità = 0): {len(df) - len(df_filtered)}")
    print(f"Punti utilizzati: {len(df_filtered)}\n")

    crea_grafici_analisi(df_filtered, col1, col2, titolo_col1, titolo_col2,
                         f'Analisi senza entrambe gravità = 0\n(n={len(df_filtered)} punti)')

    # ============================================
    # CREAZIONE HEATMAP DELLE DIFFERENZE
    # ============================================
    
    print("\n-----------------------")
    print("CREAZIONE HEATMAP DIFFERENZE")
    
    # Nome file heatmap basato sul file di input
    nome_base = os.path.splitext(nome_file)[0]
    output_html = f"7.Analisi dati/heatmap_{nome_base}.html"
    
    centro_parma = [44.801485, 10.3279036]
    mappa = folium.Map(location=centro_parma, zoom_start=13)
    
    # Heatmap per sovrastima (differenza > 0) - OpenData > Calcolata
    df_pos = df[df['differenza'] > 0]
    if not df_pos.empty:
        HeatMap(df_pos[['latitudine', 'longitudine', 'differenza']].values.tolist(),
                radius=40, blur=25, max_zoom=13,
                gradient={0.33: 'yellow', 0.66: 'orange', 1: 'red'},
                name='Sottostima esperimento (OpenData > Calcolata)').add_to(mappa)
    
    # Heatmap per sottostima (differenza < 0) - OpenData < Calcolata
    df_neg = df[df['differenza'] < 0]
    if not df_neg.empty:
        HeatMap(df_neg[['latitudine', 'longitudine', 'differenza']].abs().values.tolist(),
                radius=40, blur=25, max_zoom=13,
                gradient={0.33: 'lightblue', 0.66: 'blue', 1: 'violet'},
                name='Sovrastima esperimento (OpenData < Calcolata)').add_to(mappa)
    
    folium.LayerControl().add_to(mappa)
    mappa.save(output_html)
    print(f"Heatmap salvata in: {output_html}")
    print(f"  Punti sovrastimati (diff < 0): {len(df_neg)}")
    print(f"  Punti sottostimati (diff > 0): {len(df_pos)}")
    print(f"  Punti con diff = 0: {len(df[df['differenza'] == 0])}")

    # ============================================
    # GRAFICI DI DISTRIBUZIONE NORMALIZZATA
    # ============================================
    
    print("\n-----------------------")
    print("CREAZIONE GRAFICI DISTRIBUZIONE NORMALIZZATA")
    
    # Filtra i dati escludendo gravità = 0
    df_opendata_nonzero = df[df[col2] != 0][col2]
    df_calcolata_nonzero = df[df[col1] != 0][col1]
    
    # Calcola IQR per entrambi i dataset
    import numpy as np
    q1_op, q3_op = np.percentile(df_opendata_nonzero, [25, 75])
    q1_calc, q3_calc = np.percentile(df_calcolata_nonzero, [25, 75])
    iqr_op = q3_op - q1_op
    iqr_calc = q3_calc - q1_calc
    
    # Calcola bins con bin_width = 0.05 (adatto per valori normalizzati 0-1)
    bin_width = 0.05
    bins_opendata = int((df_opendata_nonzero.max() - df_opendata_nonzero.min()) / bin_width) + 1
    bins_calcolata = int((df_calcolata_nonzero.max() - df_calcolata_nonzero.min()) / bin_width) + 1
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Istogramma OpenData normalizzato con frequenze relative percentuali
    n1, bins1, _ = ax1.hist(df_opendata_nonzero, bins=bins_opendata, color='steelblue', 
                        edgecolor='black', alpha=0.7, weights=np.ones(len(df_opendata_nonzero)) / len(df_opendata_nonzero) * 100)
    ax1.set_xlabel('Rischio incidenti OpenData')
    ax1.set_ylabel('Frequenza relativa (%)')
    ax1.set_title(f'OpenData (normalizzato)\n(n={len(df_opendata_nonzero)}, IQR={iqr_op:.2f}, Mediana={df_opendata_nonzero.median():.2f})')
    ax1.grid(True, alpha=0.3)
    
    # Istogramma Esperimento normalizzato con frequenze relative percentuali
    n2, bins2, _ = ax2.hist(df_calcolata_nonzero, bins=bins_calcolata, color='coral', 
                        edgecolor='black', alpha=0.7, weights=np.ones(len(df_calcolata_nonzero)) / len(df_calcolata_nonzero) * 100)
    ax2.set_xlabel('Rischio incidenti calcolato')
    ax2.set_ylabel('Frequenza relativa (%)')
    ax2.set_title(f'Estratta dalle informazioni testuali (normalizzato)\n(n={len(df_calcolata_nonzero)}, IQR={iqr_calc:.2f}, Mediana={df_calcolata_nonzero.median():.2f})')
    ax2.grid(True, alpha=0.3)
    
    # Sincronizza le scale con margini
    max_x_with_margin = max(df_opendata_nonzero.max(), df_calcolata_nonzero.max()) * 1.05
    max_y_with_margin = max(n1.max(), n2.max()) * 1.05
    
    ax1.set_xlim(0, max_x_with_margin)
    ax2.set_xlim(0, max_x_with_margin)
    ax1.set_ylim(0, max_y_with_margin)
    ax2.set_ylim(0, max_y_with_margin)
    
    plt.suptitle('Istogramma normalizzato dell\'indice di rischio stradale', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    print(f"Grafici distribuzione normalizzata creati")
    print(f"  OpenData: n={len(df_opendata_nonzero)}, IQR={iqr_op:.2f}, Mediana={df_opendata_nonzero.median():.2f}")
    print(f"  Calcolata: n={len(df_calcolata_nonzero)}, IQR={iqr_calc:.2f}, Mediana={df_calcolata_nonzero.median():.2f}")


if __name__ == "__main__":
    # Esempio di utilizzo diretto
    import sys
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
        titolo1 = sys.argv[2] if len(sys.argv) > 2 else "Indice pericolosità riferimento"
        titolo2 = sys.argv[3] if len(sys.argv) > 3 else "Indice pericolosità sperimentale"
        analisi_grafici_confronto(input_file, titolo1, titolo2)
    else:
        print("Uso: python grafici.py <input_file> [titolo1] [titolo2]")
        print("Il file di input deve avere le colonne: gravita_calcolata, gravita_opendata, media, differenza")


