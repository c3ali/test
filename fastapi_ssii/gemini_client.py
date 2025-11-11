import os
import httpx
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Utiliser OpenRouter avec Kimi K2
OPENROUTER_API_KEY = os.getenv("OPENROUTER_KIMI")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "moonshot/kimi-k2"  # Modèle Kimi K2 via OpenRouter

# --- Configuration ---
api_configured = False

if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY":
    print("Attention : La clé API OpenRouter n'est pas configurée.")
else:
    api_configured = True
    print(f"OpenRouter configuré avec le modèle: {MODEL_NAME}")


# --- Fonctions d'appel à l'API ---

def generate_with_gemini(prompt: str) -> str:
    """
    Appel SYNCHRONE à l'API OpenRouter (compatibilité avec ancien nom).
    """
    if not api_configured:
        raise RuntimeError("Client OpenRouter non configuré. Vérifiez que OPENROUTER_KIMI est définie.")

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        with httpx.Client(timeout=120.0) as client:
            response = client.post(OPENROUTER_API_URL, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

    except httpx.HTTPError as e:
        print(f"Erreur HTTP OpenRouter (sync) : {e}")
        raise RuntimeError(f"Erreur lors de l'appel à l'API OpenRouter: {e}") from e
    except Exception as e:
        print(f"Erreur OpenRouter (sync) : {e}")
        raise RuntimeError(f"Erreur lors de l'appel à l'API OpenRouter: {e}") from e

async def generate_with_gemini_async(prompt: str) -> str:
    """
    Appel ASYNCHRONE à l'API OpenRouter (compatibilité avec ancien nom).
    """
    if not api_configured:
        raise RuntimeError("Client OpenRouter non configuré. Vérifiez que OPENROUTER_KIMI est définie.")

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

    except httpx.HTTPError as e:
        print(f"Erreur HTTP OpenRouter (async) : {e}")
        raise RuntimeError(f"Erreur lors de l'appel à l'API OpenRouter: {e}") from e
    except Exception as e:
        print(f"Erreur OpenRouter (async) : {e}")
        raise RuntimeError(f"Erreur lors de l'appel à l'API OpenRouter: {e}") from e
