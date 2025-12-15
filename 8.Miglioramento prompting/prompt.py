from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, csv, json, os, re

model_id = "Qwen/Qwen2.5-1.5B-Instruct"

local_model_path = "./local_model"
device = "cuda" if torch.cuda.is_available() else "cpu"

# Caricamento modello
if os.path.exists(local_model_path):
    tokenizer = AutoTokenizer.from_pretrained(local_model_path)
    model = AutoModelForCausalLM.from_pretrained(local_model_path).to(device)
else:
    print("Scaricando modello per la prima volta...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
    tokenizer.save_pretrained(local_model_path)
    model.save_pretrained(local_model_path)
    print("Modello salvato!")

# ESEMPI

examples = {
    "localizzazione": [
        ("Scontro frontale in via Togliatti a Langhirano.", 1),
        ("Sul posto sono arrivati i soccorritori del 118 e la polizia stradale.", 0),
        ("Il ferito è stato trasportato al pronto soccorso di Parma in condizioni gravi.", 0),
        ("Il conducente ha perso il controllo e è andato a sbattere contro il guardrail.", 0),
    ],
    "tempo": [
        ("E' accaduto tutto stamattina, 14 aprile, intorno alle 8,30.", 1),
        ("Il conducente ha perso il controllo del veicolo, che è uscito dalla carreggiata.", 0),
        ("Il bilancio del terribile scontro di ieri pomeriggio è stato pesante.", 1),
        ("Si sta cercando di ricostruire la dinamica dell'incidente.", 0),
    ],
    "grave": [
        ("Incidente mortale: la vittima è un ciclista 85enne deceduto dopo il ricovero.", 1),
        ("Grave incidente stradale nel primo pomeriggio lungo l'autostrada A1.", 1),
        ("Il ferito è stato trasportato al pronto soccorso di Parma.", 0),
        ("La persona ferita avrebbe riportato traumi di media gravità.", 0),
    ],
    "moto": [
        ("Paura per un motociclista caduto a Baganzola.", 1),
        ("Il conducente ha perso il controllo del camion ed è andato addosso ad una bicicletta.", 0),
        ("Il conducente della moto sarebbe caduto rovinosamente sull'asfalto.", 1),
        ("Paura per un ciclista caduto a Baganzola.", 0),
    ],
    "utenti_deboli": [
        ("All'interno dell'auto anche due bambini, che sono rimasti miracolosamente illesi.", 1),
        ("L'altro conducente non ha riportato ferite.", 0),
        ("Il frontale tra due auto non ha purtroppo lasciato scampo all'anziana 82enne.", 1),
        ("Il conducente dell'auto è rimasto ferito mentre il camionista è rimasto illeso.", 0),
    ]
}

def analyze_label(phrase, label, prompt_text, num_examples=4):
    # Costruisci testo con esempi più contrastivi e vari
    examples_text = "Ecco alcuni esempi di riferimento (1 = sì, 0 = no):\n\n"
    for example, value in examples[label][:num_examples]:
        examples_text += f'- "{example}" → {value}\n'
    examples_text += "\n"

    # Prompt principale
    messages = [
        {
            "role": "system",
            "content": (
                f"Rispondi solo con un JSON valido. "
                f"Usa come etichetta: \"{label}\". "
                "Usa come valore: 0 o 1."
            )
        },
        {
            "role": "user",
            "content": (
                "Sei un analista che etichetta frasi di articoli su incidenti stradali per un archivio giornalistico.\n\n"
                f"Decidi se la seguente frase soddisfa la condizione: {prompt_text}\n\n"
                "Controlla se la frase fornisce prove chiare (esplicite o implicite). "
                "Se non trovi elementi sufficienti, rispondi 0.\n\n"
                "Esempi di riferimento per comprendere la logica decisionale:\n"
                f"{examples_text}"
                f"Frase da analizzare: '{phrase}'\n\n"
                "Rispondi solo con il JSON richiesto."
            )
        }
    ]
    
    # Costruzione prompt finale
    prompt = ""
    for msg in messages:
        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"

    # Generazione modello
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=64,
        temperature=0.2,
        top_p=0.6,
        top_k=40,
        pad_token_id=tokenizer.eos_token_id
    )

    # Parsing del JSON
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    
    result = {label: 'n'}
    json_candidates = re.findall(r"\{.*?\}", response, re.DOTALL)
    for candidate in json_candidates:
        candidate_fixed = candidate.replace("'", '"')
        try:
            parsed = json.loads(candidate_fixed)
            if label not in parsed:
                continue
            if str(parsed[label]) not in ["0", "1"] and parsed[label] not in [0, 1]:
                continue
            result = {label: int(parsed[label])}
            break
        except Exception:
            continue
    return result[label] if result[label] in [0, 1] else 0


# Prompt per ogni etichetta
label_prompts = {
    "localizzazione": (
        "La frase menziona il LUOGO SPECIFICO dell'incidente (via/strada con nome proprio, città, frazione, chilometro autostrada)? "
        "NON considerare: 'sul posto' (generico), ospedali/pronto soccorso (destinazioni post-incidente), "
        "'strada/carreggiata/guardrail/tangenziale' senza nome specifico."
    ),
    "tempo": "La frase indica quando è avvenuto l'incidente (data, ora, periodo del giorno)?",
    "grave": (
        "La frase indica conseguenze GRAVI dell'incidente (morte/decesso/vittima, condizioni critiche, codice rosso, "
        "prognosi riservata, pericolo di vita, o esplicitamente 'grave/gravi/gravissimo')? "
        "NON considerare grave: trasporto generico in ospedale/pronto soccorso, 'media gravità' (= non grave), "
        "intervento 118/soccorsi senza indicatori di gravità."
    ),
    "moto": "La frase riguarda moto, scooter o motorini?",
    "utenti_deboli": "La frase menziona pedoni, ciclisti, bambini o anziani coinvolti?"
}

# ============================================================
# funzioni utili per modifica prompt/esempi
# ============================================================

def modifica_prompt():
    """Funzione per modificare i prompt delle etichette"""
    print("\n--- MODIFICA PROMPT ---")
    print("\nPrompt attuali:")
    print('label_prompts = {')
    for label, prompt in label_prompts.items():
        print(f'    "{label}": "{prompt}",')
    print('}')
    
    print("\nReinserisci tutti i prompt (5 righe, una per etichetta):")
    print("Formato: etichetta: testo del prompt")
    
    nuovi_prompts = {}
    for label in label_prompts.keys():
        linea = input(f"{label}: ").strip()
        if linea:
            nuovi_prompts[label] = linea
        else:
            nuovi_prompts[label] = label_prompts[label]
    
    label_prompts.update(nuovi_prompts)
    print("\nPrompt aggiornati. Rianalisi della frase corrente...")


def modifica_esempi(num_examples=4):
    """Funzione per modificare gli esempi delle etichette"""
    print("\n--- MODIFICA ESEMPI ---")
    print("Quale etichetta vuoi modificare?")
    for i, label in enumerate(examples.keys(), 1):
        num_esempi = len(examples[label])
        print(f"{i}. {label} ({num_esempi} esempi)")
    
    scelta = input("\nNumero (INVIO per annullare): ").strip()
    if scelta.isdigit():
        label_list = list(examples.keys())
        label_idx = int(scelta) - 1
        if 0 <= label_idx < len(label_list):
            label = label_list[label_idx]
            
            print(f"\n--- Esempi attuali per '{label}' ---")
            print(f'esempi "{label}":')
            for frase, valore in examples[label]:
                print(f'    ("{frase}", {valore})')
            print('')
            
            print(f"\nInserisci {num_examples} esempi nel formato:")
            print('    ("frase", valore),')
            print()
            
            nuovi_esempi = []
            for i in range(num_examples):
                linea = input(f"Esempio {i+1}: ").strip()
                # Parse della riga: ("frase", valore)
                try:
                    # Rimuovi spazi e parentesi iniziali/finali
                    linea = linea.strip().strip('(),')
                    # Trova le virgolette della frase
                    if '"' in linea:
                        parts = linea.split('"')
                        frase = parts[1]
                        valore = parts[2].strip().strip(',').strip()
                    else:
                        print(f"Formato non valido. Usa: (\"frase\", valore)")
                        continue
                    
                    if valore in ["0", "1"]:
                        nuovi_esempi.append((frase, int(valore)))
                    else:
                        print(f"Valore deve essere 0 o 1")
                except Exception as e:
                    print(f"Errore nel parsing: {e}. Riprova.")
            
            if nuovi_esempi:
                examples[label] = nuovi_esempi
                print(f"\nesempi aggiornati")
            else:
                print("\nNessuna modifica effettuata.")
    
    print("Rianalisi della frase corrente...")


# ============================================================
# output principale
# ============================================================

print("\n" + "="*60)
print("ANALISI FRASI DAL FILE DIFFERENZE")
print("="*60)
print("Comandi disponibili:")
print("  INVIO  - Analizza la prossima frase")
print("  1      - Modifica i prompt delle etichette")
print("  2      - Modifica gli esempi")
print("  'exit' - Esci dal programma")
print("="*60 + "\n")

# Leggi il file differenze.csv
with open("8.Miglioramento prompting/differenze.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    headers = next(reader)  # Prima riga con le intestazioni
    rows = list(reader)

# Lista delle etichette
etichette = ['localizzazione', 'tempo', 'grave', 'moto', 'utenti_deboli']

# Processa una frase alla volta
idx = 1
while idx <= len(rows):
    row = rows[idx - 1]
    
    # Aspetta input utente
    user_input = input("invio=prx, esc=exit, 1=mod prompt, 2=mod es: ").strip()
    
    if user_input.lower() in ['exit', 'quit']:
        print("\nUscita dal programma.")
        break
    
    # Modifica prompt
    if user_input.lower() == '1':
        idx -= 1
        modifica_prompt()
        continue
    
    # Modifica esempi
    if user_input.lower() == '2':
        idx -= 1
        modifica_esempi()
        continue
    
    # Se non è un comando, procedi con l'analisi
    frase = row[0]
    
    # Leggi etichette benchmark ed esperimento dal CSV
    # Formato: frase, loc_bench, loc_ris, tempo_bench, tempo_ris, grave_bench, grave_ris, moto_bench, moto_ris, deboli_bench, deboli_ris
    etichette_benchmark = {
        "localizzazione": int(row[1]),
        "tempo": int(row[3]),
        "grave": int(row[5]),
        "moto": int(row[7]),
        "utenti_deboli": int(row[9])
    }
    
    etichette_esperimento = {
        "localizzazione": int(row[2]),
        "tempo": int(row[4]),
        "grave": int(row[6]),
        "moto": int(row[8]),
        "utenti_deboli": int(row[10])
    }
    
    print("\n" + "_"*50)
    print(f"FRASE #{idx}/{len(rows)}: ")
    print(f"{frase}\n")
    
    print("\nETICHETTE BENCHMARK: loc, tmp, grav, moto, deboli")
    for etichetta in etichette:
        valore = etichette_benchmark[etichetta]
        print(f"{valore}", end=", ")
    print()
    # Mostra etichette esperimento
    for etichetta in etichette:
        valore = etichette_esperimento[etichetta]
        print(f"{valore}", end=", ")
    print("\n" + "_"*30)
    # Analizza con il modello LLM
    
    etichette_qwen = {}
    for label, prompt_text in label_prompts.items():
        value = analyze_label(frase, label, prompt_text)
        etichette_qwen[label] = value
    
    # Mostra risultati analisi Qwen
    for etichetta in etichette:
        valore = etichette_qwen[etichetta]
        print(f"{valore}", end=", ")
    
    print("\n" + "_"*50)
    
    # Incrementa idx solo dopo aver completato l'analisi
    idx += 1