import csv, re

input_file = "0. Preparazione Dataset/articoli_parma.txt"
output_pool_articoli = "0. Preparazione Dataset/dataset_articoli_frasi.csv"

def estrai_corpo(lines):
    # Trova la riga che inizia con ~ (data)
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("~"):
            start_idx = idx
            break
    if start_idx is None or start_idx == len(lines) - 1:
        return ""
    # Prendi tutte le righe DOPO la data (esclude la riga data stessa)
    corpo = [l.strip() for l in lines[start_idx + 1:] if l.strip()]
    # Escludi righe "IN AGGIORNAMENTO" e "© Riproduzione riservata."
    corpo = [l for l in corpo if not l.upper().startswith("IN AGGIORNAMENTO") and l != "© Riproduzione riservata."]
    return " ".join(corpo)

with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

raw_articles = content.split('--- .')

with open(output_pool_articoli, "w", newline="", encoding="utf-8") as f_art:

    writer_art = csv.writer(f_art, delimiter=';')
    header = ["articolo", "localizzazione", "tempo", "grave", "moto", "utenti_deboli"]
    # Aggiungi la colonna articolo_id solo per il secondo file
    header_art = ["articolo_id"] + header
    writer_art.writerow(header_art)

    articolo_id = 1
    for idx, raw_article in enumerate(raw_articles):
        article = raw_article.strip()
        if not article:
            continue

        lines = article.splitlines()
        article_text = estrai_corpo(lines)
        article_text = re.sub(r'[\x00-\x1F\x7F]', ' ', article_text)
        article_text = article_text.replace('\xa0', ' ')
        article_text = " ".join(article_text.split())

        if article_text:
            # Dividi l'articolo in frasi usando il punto come delimitatore
            sentences = re.split(r'\.(?=\s|$)', article_text)
            
            # Pulisci e filtra le frasi
            cleaned_sentences = []
            for sentence in sentences:
                sentence = sentence.strip()
                # Ignora frasi vuote, con meno di 2 parole e quelle che contengono "© Riproduzione riservata"
                if sentence and len(sentence.split()) > 2 and "© Riproduzione riservata" not in sentence:  
                    # Aggiungi il punto a fine frase
                    sentence += '.'
                    cleaned_sentences.append(sentence)
            
            # Scrivi ogni frase come una riga separata
            for sentence in cleaned_sentences:
                row = [sentence, 0, 0, 0, 0, 0]
                writer_art.writerow([articolo_id] + row)
            
            # Incrementa l'ID articolo solo dopo aver scritto tutte le frasi
            articolo_id += 1

print(f"Estrazione e divisione in frasi completa.\nDataset salvato")