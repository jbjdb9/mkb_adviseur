import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("OPENWEBUI_BASE_URL")
API_KEY = os.getenv("OPENWEBUI_API_KEY")
MODEL_ID = os.getenv("OPENWEBUI_MODEL_ID")

print(f"BASE_URL: {BASE_URL}")
print(f"MODEL_ID: {MODEL_ID}")
print(f"API_KEY begint met: {API_KEY[:10] if API_KEY else 'LEEG'}")

# Test 1: is de server bereikbaar?
try:
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"\nServer bereikbaar: {r.status_code} - {r.text}")
except Exception as e:
    print(f"\nServer NIET bereikbaar: {e}")

# Test 2: werkt de API key?
try:
    r = requests.get(
        f"{BASE_URL}/api/models",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=5
    )
    print(f"\nAPI key werkt: {r.status_code}")
    modellen = r.json().get("data", [])
    print("Beschikbare modellen:")
    for m in modellen:
        print(f"  - {m['id']}")
except Exception as e:
    print(f"\nAPI key fout: {e}")

# Test 3: stuur een simpele chat zonder kennisbank
try:
    r = requests.post(
        f"{BASE_URL}/api/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": "Zeg alleen: hallo"}]
        },
        timeout=300
    )
    print(f"\nChat werkt: {r.status_code}")
    print(r.json()["choices"][0]["message"]["content"])
except Exception as e:
    print(f"\nChat fout: {e}")