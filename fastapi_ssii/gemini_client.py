import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Initialisation des clients ---
model = None
async_model = None

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
    print("Attention : La clé API Gemini n'est pas configurée.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

    # Client synchrone (pour les tâches non parallélisables comme l'analyse)
    model = genai.GenerativeModel('gemini-2.5-pro')

    # Client asynchrone (pour la génération de fichiers en parallèle)
    async_model = genai.GenerativeModel('gemini-2.5-pro')


# --- Fonctions d'appel à l'API ---

def generate_with_gemini(prompt: str) -> str:
    """
    Appel SYNCHRONE à l'API Gemini.
    """
    if model is None:
        return "Erreur : Client Gemini non configuré."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erreur Gemini (sync) : {e}")
        return f"Erreur : {e}"

async def generate_with_gemini_async(prompt: str) -> str:
    """
    Appel ASYNCHRONE à l'API Gemini.
    """
    if async_model is None:
        return "Erreur : Client Gemini asynchrone non configuré."
    try:
        response = await async_model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erreur Gemini (async) : {e}")
        return f"Erreur : {e}"
