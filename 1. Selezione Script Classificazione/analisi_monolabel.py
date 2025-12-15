from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, csv, json, os, re

# Load model directly
# model_id = "Qwen/Qwen3-4B-Instruct-2507"
model_id = "Qwen/Qwen2.5-1.5B-Instruct"

local_model_path = "./local_model"
device = "cuda" if torch.cuda.is_available() else "cpu"

# Controlla se il modello esiste già in locale
if os.path.exists(local_model_path):
    tokenizer = AutoTokenizer.from_pretrained(local_model_path)
    model = AutoModelForCausalLM.from_pretrained(local_model_path).to(device)
else:
    print("Scaricando modello per la prima volta...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
    
    # Salva il modello in locale
    tokenizer.save_pretrained(local_model_path)
    model.save_pretrained(local_model_path)
    print("Modello salvato!")

def analyze_label(phrase, label, prompt_text):
    messages = [
        {
            "role": "system",
            "content": (
                f"Rispondi solo con un json valido. "
                f"Usa come etichetta: \"{label}\". "    # nome label usata
                "Usa come valore: 0 o 1."
            )
        },
        {
            "role": "user",
            "content": (
                "Sei un analista che categorizza articoli di incidenti stradali per un database giornalistico.\n"
                "Classifica questa frase l'etichetta binaria seguente per organizzare le notizie di incidenti stradali:\n"
                f"Frase: '{phrase}'\n\n"  # frase del dataset
                "Rispondi alla domanda di classificazione binaria che ti pongo con 1 se la risposta è si, 0 se la risposta è no:\n"
                f"{prompt_text}\n"  # domanda del prompt
                "Risposta:"
            )
        }
    ]
    prompt = ""
    for msg in messages:
        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=64,
        temperature=0.3,
        top_p=0.7,
        pad_token_id=tokenizer.eos_token_id
    )

    # decoding e parsing della risposta 
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

# Definizione dei prompt per ogni label
label_prompts = {
    "localizzazione": "Si capisce dove è avvenuto l'incidente?",
    "tempo": "Ci sono riferimenti temporali?",
    "grave": "L'incidente ha conseguenze serie (vittime, feriti gravi, ricoveri, traumi significativi)?",
    "moto": "Sono coinvolti moto, scooter, motorini o simili?",
    "utenti_deboli": "Sono coinvolti pedoni, ciclisti o altre categorie deboli?"
}

# ------------------------------------------------------------------------------------------

file_output = "prompt6_monolabel.csv"

with open(file_output, "w", encoding="utf-8", newline="") as new_file:
    writer = csv.writer(new_file, delimiter=";")
    writer.writerow(["frase"] + list(label_prompts.keys()))

with open("dataset_ridotto_200.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    next(reader, None)  # Salta header

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