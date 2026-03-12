import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OPENWEBUI_BASE_URL")
API_KEY = os.getenv("OPENWEBUI_API_KEY")
MODEL_ID = os.getenv("OPENWEBUI_MODEL_ID")

KENNISBANK_IDS = {
    "HBO": os.getenv("KENNISBANK_HBO"),
    "MBO": os.getenv("KENNISBANK_MBO"),
    "WO": os.getenv("KENNISBANK_WO"),
}


def query_openwebui(niveau: str, systeem_prompt: str, gebruiker_prompt: str) -> str:
    """
    Stuurt een query naar OpenWebUI met de juiste kennisbank(en).
    niveau: "MBO", "HBO", "WO" of "Weet ik niet"
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # Selecteer kennisbank(en) op basis van niveau
    if niveau in KENNISBANK_IDS:
        collection_ids = [KENNISBANK_IDS[niveau]]
    else:
        # "Weet ik niet" -> zoek in alle drie
        collection_ids = [v for v in KENNISBANK_IDS.values() if v]

    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": systeem_prompt},
            {"role": "user", "content": gebruiker_prompt},
        ],
        "files": [
            {"type": "collection", "id": cid} for cid in collection_ids
        ],
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/completions",
            headers=headers,
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.ConnectionError:
        return "Kan geen verbinding maken met OpenWebUI. Controleer of de server draait en het adres klopt in .env."
    except requests.exceptions.Timeout:
        return "OpenWebUI reageert niet op tijd. Probeer het opnieuw."
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return "API key is ongeldig. Controleer OPENWEBUI_API_KEY in .env."
        return f"Fout van OpenWebUI: {e}"
    except Exception as e:
        return f"Onverwachte fout: {e}"