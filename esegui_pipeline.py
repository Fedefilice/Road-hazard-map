#!/usr/bin/env python3
"""
Script per eseguire la pipeline completa dalle cartelle 5, 6 e 7
"""
import subprocess
import sys
from pathlib import Path

def run_script(script_path):
    """Esegue uno script Python e gestisce eventuali errori"""
    print(f"\n{'='*60}")
    print(f"Esecuzione: {script_path}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✓ Completato: {script_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Errore durante l'esecuzione di {script_path.name}")
        print(f"Codice di uscita: {e.returncode}")
        return False

def main():
    base_path = Path(__file__).parent
    
    # Definizione degli script da eseguire in ordine
    scripts = [
        # Cartella 5: Pipeline Dataset
        base_path / "5.Pipeline_Dataset" / "1.raffinazione_risultati.py",
        base_path / "5.Pipeline_Dataset" / "2.Geolocalizzazione.py",
        
        # Cartella 6: Mappa OpenData
        base_path / "6. Mappa OpenData" / "ripulisci_colonne.py",
        base_path / "6. Mappa OpenData" / "3.gravita+heatmap_opendata.py",
        base_path / "5.Pipeline_Dataset" / "3.gravita+heatmap_esperimento.py",
        
        # Cartella 7: Analisi dati
        base_path / "7.Analisi dati" / "1.unione_gravita.py",
        base_path / "7.Analisi dati" / "2.distribuzione.py",
        base_path / "7.Analisi dati" / "3.gestione_sbilanciamento.py",
        base_path / "7.Analisi dati" / "4.esegui_grafici.py",
    ]
    
    print("\n" + "="*60)
    print("ESECUZIONE PIPELINE COMPLETA")
    print("="*60)
    
    success_count = 0
    failed_scripts = []
    
    for script in scripts:
        if not script.exists():
            print(f"\nScript non trovato: {script}")
            failed_scripts.append(script.name)
            continue
            
        if run_script(script):
            success_count += 1
        else:
            failed_scripts.append(script.name)
            response = input("\nContinuare con il prossimo script? (s/n): ")
            if response.lower() != 's':
                print("\nPipeline interrotta dall'utente.")
                break
    
    # Riepilogo finale
    print("\n" + "="*60)
    print("RIEPILOGO ESECUZIONE")
    print("="*60)
    print(f"Script eseguiti con successo: {success_count}/{len(scripts)}")
    
    if failed_scripts:
        print(f"\nScript con errori o non trovati:")
        for script in failed_scripts:
            print(f"  - {script}")
    else:
        print("\n✓ Tutti gli script sono stati eseguiti con successo!")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
