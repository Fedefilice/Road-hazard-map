import pandas as pd
from sklearn.metrics import f1_score, accuracy_score

def calculate_metrics_per_label_from_files(true_labels_path, predicted_labels_path):
    """
    Calcola Accuratezza, F1-score macro e weighted per ogni etichetta leggendo i dati da file CSV.

    Args:
        true_labels_path (str): Percorso del file CSV contenente le etichette vere.
        predicted_labels_path (str): Percorso del file CSV contenente le etichette predette.

    Returns:
        dict: Un dizionario dove le chiavi sono i nomi delle etichette e i valori sono dizionari
              contenenti 'accuracy', 'f1_macro', 'f1_weighted'.
              Ritorna None se ci sono discrepanze nelle colonne o nella lunghezza dei dati.
    """
    try:
        true_df = pd.read_csv(true_labels_path, sep=';')
        predicted_df = pd.read_csv(predicted_labels_path, sep=';')
    except FileNotFoundError:
        print("Errore: Uno o entrambi i file non trovati. Controlla i percorsi.")
        return None
    except Exception as e:
        print(f"Errore durante la lettura dei file: {e}")
        return None

    # Identifica le colonne delle etichette (escludendo 'frase' se presente)
    label_columns_true = true_df.columns[1:] if 'frase' in true_df.columns else true_df.columns
    label_columns_pred = predicted_df.columns[1:] if 'frase' in predicted_df.columns else predicted_df.columns

    if not label_columns_true.equals(label_columns_pred):
        print("Errore: I nomi delle colonne nei dati veri e predetti non corrispondono.")
        return None

    if len(true_df) != len(predicted_df):
        print("Errore: Il numero di righe nei dati veri e predetti non corrisponde.")
        return None

    metrics = {}
    for column in label_columns_true:
        true_labels = true_df[column]
        predicted_labels = predicted_df[column]
        
        # Calcola le metriche
        accuracy = accuracy_score(true_labels, predicted_labels)
        f1_macro = f1_score(true_labels, predicted_labels, average='macro')
        f1_weighted = f1_score(true_labels, predicted_labels, average='weighted')
        
        metrics[column] = {
            'accuracy': accuracy,
            'f1_macro': f1_macro,
            'f1_weighted': f1_weighted
        }

    return metrics


true_data_filepath = "./3 Risultati-f1 calc/dataset_etichettato_900.csv"
predicted_data_filepath = "./3 Risultati-f1 calc/prompt6_monolabel_few.csv"

# Calcola le metriche
print(f"Caricamento delle etichette vere da: {true_data_filepath}")
print(f"Caricamento delle etichette predette da: {predicted_data_filepath}")
results = calculate_metrics_per_label_from_files(true_data_filepath, predicted_data_filepath)

if results:
    print("\nMetriche per etichetta:")
    print(f"{'Label':<15}\t {'Accuratezza':<12} \t{'F1 medio':<10} \t{'F1 ponderato':<12}")
    print("-" * 50)
    for label, metrics in results.items():
        accuracy_pct = metrics['accuracy'] * 100
        print(f"{label:<15}\t {accuracy_pct:.2f}\t {metrics['f1_macro']:.2f}\t {metrics['f1_weighted']:.2f}")
