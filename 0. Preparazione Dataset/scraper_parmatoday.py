import requests, time
from bs4 import BeautifulSoup

def scrape_article(article_url):
    try:
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trova il titolo
        title_tag = soup.find('h1', class_='entry-title')
        
        if not title_tag:
            title_tag = soup.find('h1')
        
        title = title_tag.get_text(strip=True) if title_tag else "Titolo non trovato"
        
        # Trova la data con pattern regex italiano
        import re
        date = None
        date_pattern = re.compile(r'\d{1,2}\s+(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+\d{4}\s+\d{1,2}:\d{2}')
        all_text_elements = soup.find_all(['p', 'span', 'div', 'time'])
        
        for elem in all_text_elements:
            text = elem.get_text(strip=True)
            match = date_pattern.search(text)
            if match:
                date = match.group()
                break
        
        if not date:
            date = "Data non trovata"
        
        # Trova il contenuto dell'articolo
        content_div = soup.find('article')
        
        if content_div:
            # Rimuovi elementi non necessari come script, style, ecc.
            for script in content_div(['script', 'style', 'iframe']):
                script.decompose()
            
            # Estrai il testo
            paragraphs = content_div.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs])
        else:
            content = "Contenuto non trovato"
        
        # Formatta l'output come nel file di esempio
        formatted_output = f"#{article_url}\n{title}. \n~ {date}. \n{content}\n--- . "
        
        return formatted_output
    
    except Exception as e:
        print(f"Errore durante lo scraping di {article_url}: {str(e)}")
        return None


def scrape_page(page_url):
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trova tutti i link agli articoli
        article_links = []
        
        # Cerca gli articoli nella pagina
        articles = soup.find_all('article')
        
        for article in articles:
            # Trova tutti i link nell'articolo
            all_links = article.find_all('a', href=True)
            
            # Cerca il link più specifico (quello con il nome dell'articolo)
            best_link = None
            for link in all_links:
                href = link['href']
                
                # Salta link generici che finiscono con solo "/"
                if href.endswith('/') and not href.endswith('.html'):
                    continue
                
                # Cerca link che contengono info sull'articolo
                if '.html' in href or 'incidente' in href.lower():
                    # Assicurati che sia un URL completo
                    if not href.startswith('http'):
                        href = 'https://www.parmatoday.it' + href
                    best_link = href
                    break  # Prendi il primo link specifico
            
            # Aggiungi il link se trovato
            if best_link and best_link not in article_links:
                article_links.append(best_link)
        
        return article_links
    
    except Exception as e:
        print(f"Errore durante lo scraping della pagina {page_url}: {str(e)}")
        return []


def main():
    """
    Funzione principale che orchestra lo scraping
    """
    start_page = 1
    end_page = 119
    # URL base per la ricerca con filtro temporale 2016-2022
    base_url_page1 = "https://www.parmatoday.it/search/channel/cronaca/from/2016-01-01/to/2022-12-31/query/incidenti+stradali"
    base_url_other = "https://www.parmatoday.it/search/channel/cronaca/from/2016-01-01/to/2022-12-31/query/incidenti+stradali/pag/{}"
    
    output_file = "articoli_parma.txt"
    
    print(f"Inizio scraping da pagina {start_page} a pagina {end_page}")
    print(f"Output salvato in: {output_file}")
    
    all_articles = []
    
    # Scorri tutte le pagine
    for page_num in range(start_page, end_page + 1):
        # La prima pagina ha un URL diverso (senza /pag/1)
        if page_num == 1:
            page_url = base_url_page1
        else:
            page_url = base_url_other.format(page_num)
        print(f"\nScraping pagina {page_num}/{end_page}: {page_url}")
        
        # Ottieni gli URL degli articoli dalla pagina
        article_urls = scrape_page(page_url)
        print(f"  Trovati {len(article_urls)} articoli")
        
        # Scrape ogni articolo
        for idx, article_url in enumerate(article_urls, 1):
            print(f"  Scraping articolo {idx}/{len(article_urls)}")
            article_content = scrape_article(article_url)
            
            if article_content:
                all_articles.append(article_content)
            
            # Pausa tra le richieste per non sovraccaricare il server
            time.sleep(1)
        
        # Pausa più lunga tra le pagine
        time.sleep(2)
        
        # Salva progressivamente ogni 5 pagine
        if page_num % 5 == 0:
            print(f"\n  Salvataggio intermedio dopo pagina {page_num}...")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_articles))
    
    # Salvataggio finale
    print(f"\nScraping completato! Salvati {len(all_articles)} articoli")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_articles))
    
    print(f"File salvato: {output_file}")


if __name__ == "__main__":
    main()