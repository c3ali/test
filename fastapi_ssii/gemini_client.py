import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API depuis les variables d'environnement
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configurer l'API Gemini
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
    print("Attention : La clé API Gemini n'est pas configurée.")
    # On peut soit lever une exception, soit continuer avec un client non fonctionnel
    # Pour le moment, on affiche un avertissement.
    model = None
else:
    genai.configure(api_key=GEMINI_API_KEY)
    # Mise à jour vers un modèle plus récent et stable
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

def generate_with_gemini(prompt: str) -> str:
    """
    Envoie un prompt à l'API Gemini et retourne la réponse textuelle.

    Args:
        prompt: Le prompt à envoyer au modèle.

    Returns:
        La réponse générée par le modèle, ou un message d'erreur si l'API n'est pas configurée.
    """
    if model is None:
        return "Erreur : Le client Gemini n'est pas configuré. Veuillez vérifier votre clé API."

    try:
        response = model.generate_content(prompt)
        # Nettoyer la réponse pour enlever les potentiels marqueurs de formatage non désirés
        return response.text.strip()
    except Exception as e:
        print(f"Une erreur est survenue lors de l'appel à l'API Gemini : {e}")
        return f"Erreur lors de la génération de contenu : {e}"
