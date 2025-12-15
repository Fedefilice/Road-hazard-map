from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, csv, json, os, re

model_id = "Qwen/Qwen3-4B-Instruct-2507"

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
        ("La sua auto si è schiantata contro una pianta in località Baracca Ceno.", 1),
        ("Come sindaco e come rappresentante della comunità ci tengo a ricordarlo.", 0),
        ("Scontro frontale in via Togliatti a Langhirano.", 1),
        ("Al momento, nel tratto interessato, il traffico è regolare.", 0),
    ],
    "tempo": [
        ("E' accaduto tutto stamattina, 14 aprile, intorno alle 8,30.", 1),
        ("Il conducente ha perso il controllo del veicolo, che è uscito dalla carreggiata.", 0),
        ("Il bilancio del terribile scontro di ieri pomeriggio è stato pesante.", 1),
        ("Si sta cercando di ricostruire la dinamica dell'incidente.", 0),
    ],
    "grave": [
        ("Le sue condizioni di salute sono gravi ma non è in pericolo di vita.", 1),
        ("L’automobilista ha riportato solo lievi escoriazioni.", 0),
        ("I sanitari lo hanno trasportato in codice rosso al pronto soccorso dell'Ospedale di Parma.", 1),
        ("La dinamica dell'incidente non è ancora chiara.", 0),
    ],
    "moto": [
        ("Paura per un motociclista caduto a Baganzola.", 1),
        ("Dopo un contatto tra l'auto e il camion, il rimorchio si sarebbe ribaltato,.", 0),
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
    "localizzazione": "La frase menziona un luogo preciso dell’incidente (via, piazza, comune, frazione)?",
    "tempo": "La frase indica quando è avvenuto l’incidente (data, ora, periodo del giorno)?",
    "grave": "La frase parla di conseguenze gravi o di persone in condizioni critiche?",
    "moto": "La frase riguarda moto, scooter o motorini?",
    "utenti_deboli": "La frase menziona pedoni, ciclisti, bambini o anziani coinvolti?"
}

# -----------------------------------------------------------

file_output = "prompt_900.csv"

with open(file_output, "w", encoding="utf-8", newline="") as new_file:
    writer = csv.writer(new_file, delimiter=";")
    writer.writerow(["frase"] + list(label_prompts.keys()))

with open("dataset_etichettato_900.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    next(reader, None)
    for row in reader:
        frase = row[0]
        results = []
        try:
            for label, prompt_text in label_prompts.items():
                value = analyze_label(frase, label, prompt_text)
                results.append(value)
            with open(file_output, "a", encoding="utf-8", newline="") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow([frase] + results)
        except Exception as e:
            print(f"Errore nella riga: {e}")
            with open(file_output, "a", encoding="utf-8", newline="") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow([frase] + [0]*len(label_prompts))

print("Processamento completato! Elaborate frasi.")