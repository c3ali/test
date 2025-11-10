import httpx
from pydantic import HttpUrl
from fastapi_ssii.agents import project_manager

def generation_task(description: str, webhook_url: HttpUrl):
    """
    Tâche de fond complète :
    1. Orchestre la génération du projet.
    2. Envoie le résultat final au webhook fourni.
    """
    print(f"Démarrage de la tâche de génération pour : '{description}'")

    # Étape 1 : Génération du projet
    generation_result = project_manager.generate_project(description)

    # Étape 2 : Envoi du résultat au webhook
    print(f"Génération terminée. Envoi du résultat à {webhook_url}...")
    try:
        # Utiliser un client httpx pour envoyer la requête POST
        with httpx.Client() as client:
            response = client.post(
                str(webhook_url),
                json=generation_result,
                timeout=30.0  # Définir un timeout de 30 secondes
            )
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)

        print(f"Résultat envoyé avec succès au webhook. Statut : {response.status_code}")

    except httpx.RequestError as e:
        print(f"Erreur réseau lors de la tentative d'envoi au webhook {webhook_url}: {e}")
    except httpx.HTTPStatusError as e:
        print(f"Erreur de statut HTTP lors de l'envoi au webhook {webhook_url}: {e.response.status_code} - {e.response.text}")
