import os
import httpx
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Utiliser OpenRouter avec Kimi K2
OPENROUTER_API_KEY = os.getenv("OPENROUTER_KIMI")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "moonshotai/kimi-k2-thinking"  # Modèle Kimi K2 Thinking via OpenRouter

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
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/c3ali/test",  # Requis par OpenRouter
            "X-Title": "SSII FastAPI Agent"  # Optionnel mais recommandé
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        with httpx.Client(timeout=120.0) as client:
            response = client.post(OPENROUTER_API_URL, json=payload, headers=headers)

            # Meilleur logging des erreurs
            if response.status_code != 200:
                error_detail = response.text
                print(f"[ERROR] OpenRouter API Error {response.status_code}: {error_detail}")

            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.text[:500]}"
        print(f"[ERROR] OpenRouter HTTP Error (sync): {error_msg}")
        raise RuntimeError(f"Erreur OpenRouter API: {error_msg}") from e
    except httpx.HTTPError as e:
        print(f"[ERROR] OpenRouter Network Error (sync): {e}")
        raise RuntimeError(f"Erreur réseau OpenRouter: {e}") from e
    except Exception as e:
        print(f"[ERROR] OpenRouter Unexpected Error (sync): {e}")
        raise RuntimeError(f"Erreur inattendue OpenRouter: {e}") from e

async def generate_with_gemini_async(prompt: str) -> str:
    """
    Appel ASYNCHRONE à l'API OpenRouter (compatibilité avec ancien nom).
    """
    if not api_configured:
        raise RuntimeError("Client OpenRouter non configuré. Vérifiez que OPENROUTER_KIMI est définie.")

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/c3ali/test",  # Requis par OpenRouter
            "X-Title": "SSII FastAPI Agent"  # Optionnel mais recommandé
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)

            # Meilleur logging des erreurs
            if response.status_code != 200:
                error_detail = response.text
                print(f"[ERROR] OpenRouter API Error {response.status_code}: {error_detail}")

            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.text[:500]}"
        print(f"[ERROR] OpenRouter HTTP Error (async): {error_msg}")
        raise RuntimeError(f"Erreur OpenRouter API: {error_msg}") from e
    except httpx.HTTPError as e:
        print(f"[ERROR] OpenRouter Network Error (async): {e}")
        raise RuntimeError(f"Erreur réseau OpenRouter: {e}") from e
    except Exception as e:
        print(f"[ERROR] OpenRouter Unexpected Error (async): {e}")
        raise RuntimeError(f"Erreur inattendue OpenRouter: {e}") from e
