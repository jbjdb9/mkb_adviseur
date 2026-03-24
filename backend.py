import requests
import os
from dotenv import load_dotenv
import re
import random


load_dotenv()

BASE_URL = os.getenv("OPENWEBUI_BASE_URL")
API_KEY = os.getenv("OPENWEBUI_API_KEY")

MODEL_IDS = {
    "HBO": os.getenv("MODEL_HBO"),
    "MBO": os.getenv("MODEL_MBO"),
    "WO": os.getenv("MODEL_WO"),
}

TIMEOUT = 180


def detect_niveau(query: str) -> str:
    q = query.lower()
    if "mbo" in q:
        return "MBO"
    elif "hbo" in q:
        return "HBO"
    elif "wo" in q or "universiteit" in q:
        return "WO"
    else:
        return "UNKNOWN"


def build_prompt(user_query: str) -> str:
    extra_instructie = """
Zoek ALLEEN naar volledige opleidingen. Herken een opleiding aan:
- "Opleidingsnaam"
- of duidelijke titel bovenaan
- of termen zoals "Bachelor", "Master", "Niveau"

Gebruik GEEN:
- cursussen (zoals "PLC Programmeren", "Netwerkanalyse")
- losse vakken of modules

Gebruik alleen bronnen waar de opleidingsnaam expliciet genoemd wordt.

Negeer:
- kosten
- toelating
- randinformatie

Geef maximaal 3 suggesties.
"""
    return f"{extra_instructie}\n\nVraag: {user_query}"


def call_model(model_id: str, systeem_prompt: str, gebruiker_prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": systeem_prompt},
            {"role": "user", "content": gebruiker_prompt},
        ],
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/completions",
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        content = re.sub(r'\[\d+\]', '', content)
        return content
    except requests.exceptions.ConnectionError:
        return "Kan geen verbinding maken met OpenWebUI. Controleer of de server draait en het adres klopt in .env."
    except requests.exceptions.Timeout:
        return "OpenWebUI reageert niet op tijd. Probeer het opnieuw."
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return "API key is ongeldig. Controleer OPENWEBUI_API_KEY in .env."
        return f"Fout van OpenWebUI (model {model_id}): {e}"
    except Exception as e:
        return f"Onverwachte fout bij model {model_id}: {e}"


def is_valid_response(text: str) -> bool:
    vereiste_termen = ["bachelor", "master", "niveau", "opleiding", "studie"]

    return any(term.lower() in text.lower() for term in vereiste_termen)


def query_llm(user_query: str, systeem_prompt: str, gekozen_niveau: str = None) -> str:
    niveau = gekozen_niveau if gekozen_niveau else detect_niveau(user_query)
    prompt = build_prompt(user_query)
    antwoorden = {}

    if niveau in MODEL_IDS:
        model_id = MODEL_IDS[niveau]
        result = call_model(model_id, systeem_prompt, prompt)
        print(f"[DEBUG] Niveau: {niveau}, Model: {model_id}")  #debug
        print(f"[DEBUG] Resultaat: {result[:200]}")             #debug
        if is_valid_response(result):
            return result
        else:
            return "De resultaten waren niet betrouwbaar genoeg. Probeer je vraag specifieker te maken."
    else:
        for niv, model_id in MODEL_IDS.items():
            result = call_model(model_id, systeem_prompt, prompt)
            print(f"[DEBUG] Niveau: {niv}, Model: {model_id}")          #debug
            print(f"[DEBUG] is_valid: {is_valid_response(result)}")     #ontmug
            print(f"[DEBUG] Resultaat: {result[:200]}")                 #same
            if is_valid_response(result):
                antwoorden[niv] = result
        print(f"[DEBUG] Antwoorden keys: {list(antwoorden.keys())}")    #MUG
        if not antwoorden:
            return "Geen bruikbare resultaten gevonden. Probeer je vraag anders te formuleren."
        return rank_en_combine(antwoorden)


def rank_en_combine(antwoorden: dict) -> str:
    output = "### Beste matches (gecombineerd):\n\n"

    for i, (niveau, text) in enumerate(antwoorden.items(), 1):
        output += f"**Suggestie {i} ({niveau}):**\n\n"
        output += text.strip() + "\n\n"

    return output.strip()


#Tijdelijk als losse knop voor debugging
#Het opvragen van de contactgegevens van de opleidingen die gegeven zijn

def vraag_contactgegevens(opleiding_naam: str, niveau: str, systeem_prompt: str) -> str:
    prompt = f"""
Zoek ALLEEN de contactgegevens die specifiek horen bij de opleiding: "{opleiding_naam}"

Geef indien gevonden:
- Contactpersoon (naam en/of functie)
- E-mailadres
- Telefoonnummer
- Naam van de instelling

Strikte regels:
- Geef NOOIT contactgegevens van een andere opleiding
- Als je niet zeker bent dat de gegevens bij "{opleiding_naam}" horen, geef ze dan NIET
- Als er niets gevonden kan worden, geef dan alleen de naam van de instelling 
  (indien bekend) en het advies om daar naar "{opleiding_naam}" te vragen
"""
    # Bij "weet ik niet" alle modellen proberen tot er iets nuttigs terugkomt... force >:)
    if niveau not in MODEL_IDS:
        for model_id in MODEL_IDS.values():
            result = call_model(model_id, systeem_prompt, prompt)
            if is_valid_response(result):
                return result
        return (
            f'Geen contactgegevens gevonden voor "{opleiding_naam}". '
            f'Probeer de instelling direct te contacteren en vraag naar deze opleiding.'
        )

    model_id = MODEL_IDS.get(niveau)
    if not model_id:
        return "Onbekend niveau."
    return call_model(model_id, systeem_prompt, prompt)