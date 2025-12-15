# Progetto Tirocinio - Analisi Incidenti Stradali

Questo progetto implementa una pipeline completa per l'analisi degli incidenti stradali, dalla raccolta dati alla visualizzazione dei risultati.

## Struttura del Progetto

### 0. Preparazione Dataset
Contiene script per la preparazione iniziale dei dati:
- `scraper_parmatoday.py` - Scraping articoli da ParmaToday
- `scomposizione_articoli.py` - Scomposizione articoli in frasi
- `ritaglia_dataset.py` - Riduzione del dataset
- `analizza_date.py` - Analisi temporale dei dati

### 1. Selezione Script Classificazione
Script per testare diverse strategie di classificazione:
- `analisi_monolabel.py` - Classificazione monolabel
- `analisi_multilabel.py` - Classificazione multilabel
- Varianti few-shot e simplified

### 2. Selezione HPC
Script ottimizzati per esecuzione su cluster HPC:
- Versioni numerate degli script di analisi
- `sbatch_template.sh` - Template per job SLURM

### 3. Risultati - F1 Score Calculator
Calcolo delle metriche di performance:
- `f1-score-calculator.py` - Calcolo F1-score
- File di risultati per diverse configurazioni

### 4. Script Finale 899
Script finale per l'analisi del dataset completo:
- `analisi_900.py` - Versione standard per elaborazione del dataset completo
- `dataset_etichettato_900.csv` - Dataset completo etichettato
- `prompt_900.csv` - Prompt utilizzati per l'analisi
- `risultato_prompt_900.txt` - Risultati dell'elaborazione

### 5. Pipeline Dataset
Pipeline principale per l'elaborazione dati:
1. `1.raffinazione_risultati.py` - Raffinazione dei risultati della classificazione
2. `2.Geolocalizzazione.py` - Geolocalizzazione degli incidenti
3. `3.gravita+heatmap_esperimento.py` - Calcolo gravità e generazione heatmap

### 6. Mappa OpenData
Elaborazione dati OpenData:
- `ripulisci_colonne.py` - Pulizia dati Incidenti_2016-2022.csv
- `3.gravita+heatmap_opendata.py` - Analisi e heatmap dati storici

### 7. Analisi Dati
Analisi statistica finale:
1. `1.unione_gravita.py` - Unione dataset esperimento e OpenData
2. `2.distribuzione.py` - Analisi distribuzione dati
3. `3.gestione_sbilanciamento.py` - Normalizzazione e bilanciamento
4. `4.esegui_grafici.py` - Generazione grafici finali

### 8. Miglioramento Prompting
Sperimentazione con diverse tecniche di prompting:
- `analisi_differenze.py` - Analisi delle differenze tra approcci
- `analizza_grave.py` - Analisi specifica della gravità
- `prompt.py` - Script per generazione prompt
- `differenze.csv` - Risultati delle differenze
- `prompt.txt` - Template di prompt

## Esecuzione Pipeline Completa

Per eseguire l'intera pipeline (cartelle 5-7) in sequenza automatica:

```bash
python esegui_pipeline.py
```

Lo script:
- Esegue tutti gli script in ordine
- Mostra l'avanzamento in tempo reale
- Gestisce gli errori chiedendo se continuare
- Fornisce un riepilogo finale dell'esecuzione

## File di Output Principali (Root)

- `heatmap_esperimento.html` - Mappa interattiva degli incidenti dal dataset sperimentale
- `heatmap_opendata.html` - Mappa interattiva dei dati storici OpenData
- `prompt_900.csv` - Dataset con prompt utilizzati
- `calcola_gravita.py` - Script per calcolo indice di gravità
- `crea_heatmap.py` - Script per generazione heatmap
- `correggi_indici.py` - Script per correzione indici
- `esegui_pipeline.py` - Script per esecuzione automatica pipeline completa (cartelle 5-7)

## Requisiti

- Python 3.x
- Librerie: pandas, numpy, folium, geopy, transformers, torch
- Modelli NLP locali nella cartella `local_model/`
- Modello NER in `it_nerIta_trf/`

## Note

- La cartella `cache/` contiene cache di modelli e risultati intermedi
- `__pycache__/` contiene file compilati Python
- I file `.gitignore` escludono dal versioning cartelle pesanti e temporanee
