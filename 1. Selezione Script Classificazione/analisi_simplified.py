from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, csv, json, os, re

model_id = "Qwen/Qwen3-4B-Instruct-2507"
# model_id = "Qwen/Qwen2.5-1.5B-Instruct"

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

# -------------------------------------------------------------------
# ESEMPI CORRETTI (4 per etichetta, distinti e non ambigui)
# - Ogni etichetta ha 2 esempi positivi (1) e 2 negativi (0).
# - Nessun esempio è ripetuto in entrambe le etichette.
# -------------------------------------------------------------------

examples = {
    "localizzazione": [
        ("Scontro frontale in via Togliatti a Langhirano.", 1),
        ("Un camion si è ribaltato sulla tangenziale ovest di Parma.", 1),
        ("Il traffico è stato rallentato dopo l’incidente.", 0),
        ("Le autorità stanno coordinando i soccorsi.", 0),
    ],
    "grave": [
        ("Un giovane è stato trasportato in codice rosso all’ospedale Maggiore.", 1),
        ("Grave incidente stradale in tangenziale nord: un morto e due feriti.", 1),
        ("La donna ha riportato ferite lievi e non è in pericolo di vita.", 0),
        ("L’automobilista è stato medicato sul posto e dimesso poco dopo.", 0),
    ]
}

# -------------------------------------------------------------------
# FUNZIONE DI ANALISI CON PROMPT OTTIMIZZATO PER QWEN3-4B-INSTRUCT
# (il parsing e la logica di estrazione JSON restano invariati)
# -------------------------------------------------------------------

def analyze_label(phrase, label, prompt_text, num_examples=4):
    # Blocchi di esempio chiari e contrastivi
    examples_text = "Esempi di riferimento (1 = sì, 0 = no):\n"
    for example, value in examples[label][:num_examples]:
        examples_text += f'- "{example}" → {value}\n'
    examples_text += "\n"

    # Prompt ottimizzato (regole di prompt engineering applicate)
    messages = [
        {
            "role": "system",
            "content": (
                f"Il tuo compito è etichettare frasi provenienti da articoli di cronaca su incidenti stradali. "
                f"Rispondi solo con un JSON valido. "
                f"Usa come etichetta: \"{label}\". "
                "Usa come valore: 0 o 1."
            )
        },
        {
            "role": "user",
            "content": (
                f"Domanda di classificazione:\n{prompt_text}\n\n"
                "Criteri decisionali:\n"
                "1. Assegna **1** se la frase fornisce prove esplicite o implicite ma chiare.\n"
                "2. Assegna **0** se mancano elementi concreti, la frase è generica o non pertinente.\n\n"
                f"{examples_text}"
                f"Frase da analizzare:\n\"{phrase}\"\n\n"
                "Rispondi solo con il JSON richiesto, senza testo aggiuntivo."
            )
        }
    ]

    # Costruzione prompt finale per debug
    prompt = ""
    for msg in messages:
        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"

    # Generazione
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=64,
        temperature=0.1,     # più deterministico
        top_p=0.5,           # riduce variabilità
        top_k=30,
        pad_token_id=tokenizer.eos_token_id
    )

    # Parsing del JSON (non modificato)
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

# -------------------------------------------------------------------
# PROMPT PER OGNI ETICHETTA
# -------------------------------------------------------------------

label_prompts = {
    "localizzazione": "La frase menziona un luogo preciso dell’incidente (via, piazza, comune, frazione, statale, autostrada, quartiere)?",
    "grave": "La frase indica la gravità dell’incidente (feriti gravi, codice rosso, decesso, urgenza)?",
}

# -------------------------------------------------------------------
# PIPELINE DI ELABORAZIONE FILE CSV
# -------------------------------------------------------------------

file_output = "prompt_simplified.csv"

with open(file_output, "w", encoding="utf-8", newline="") as new_file:
    writer = csv.writer(new_file, delimiter=";")
    writer.writerow(["frase"] + list(label_prompts.keys()))

with open("dataset_ridotto_200.csv", "r", encoding="utf-8") as f:
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
