from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, csv, json, os, re

# Load model directly
model_id = "Qwen/Qwen2.5-1.5B-Instruct"
# model_id = "Qwen/Qwen3-4B-Instruct-2507"

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

def analyze_incident(phrase):
    messages = [
        {
            "role": "system",
            "content": (
                "rispondi solo ed esclusivamente tramite un json valido. "
                "usa come etichette:"
                "localizzazione\", \"tempo\", \"grave\", \"moto\", \"utenti_deboli\""
                "i valori di questo json devono essere binari, quindi 0 o 1. non scrivere altro nella risposta."
            )
        },
        {
            "role": "user",
            "content": (
                "Leggi questa frase di cronaca su un incidente stradale. rispondi alle domande che ti pongo con 1 se la risposta è si, 0 se la risposta è no:\n\n"
                    "- Si capisce dove è successo?\n"
                    "- Si capisce quando è successo?\n"
                    "- L’incidente è grave?\n"
                    "- C’entra una moto?\n"
                    "- Ci sono persone vulnerabili coinvolte?\n\n"
                f"Frase: '{phrase}'\n"
                "Risposta:"
            )
        }
    ]
    # Costruzione prompt 
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

    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    result = {"localizzazione": 0, "tempo": 0, "grave": 0, "moto": 0, "utenti_deboli": 0}
    json_candidates = re.findall(r"\{.*?\}", response, re.DOTALL)
    keys = ["localizzazione", "tempo", "grave", "moto", "utenti_deboli"]
    for candidate in json_candidates:
        candidate_fixed = candidate.replace("'", '"')
        try:
            parsed = json.loads(candidate_fixed)
            if not all(k in parsed for k in keys):
                continue
            if not all(str(parsed[k]) in ["0", "1"] or parsed[k] in [0, 1] for k in keys):
                continue
            result = {k: int(parsed[k]) for k in keys}
            break
        except Exception:
            continue
    
    return result

# ----------------------------------------------------------------------------------------

# nome file di output
file_output = "prompt1_multilabel.csv"

# Crea nuovo file CSV con header
with open(file_output, "w", encoding="utf-8", newline="") as new_file:
    writer = csv.writer(new_file, delimiter=";")
    writer.writerow(["frase", "localizzazione", "tempo", "grave", "moto", "utenti_deboli"])

# MODIFICA 3: Lettura CSV semplificata
with open("dataset_ridotto_200.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    next(reader, None)  # Salta header
    
    for row in reader:
        try:
            risultati_json = analyze_incident(row[0])
            
            with open(file_output, "a", encoding="utf-8", newline="") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow([
                    row[0],
                    risultati_json['localizzazione'],
                    risultati_json['tempo'], 
                    risultati_json['grave'],
                    risultati_json['moto'],
                    risultati_json['utenti_deboli']
                ])
        except Exception as e:
            print(f"Errore nella riga: {e}")
            with open(file_output, "a", encoding="utf-8", newline="") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow([row[0], 0, 0, 0, 0, 0])

print(f"Processamento completato! Elaborate frasi.")