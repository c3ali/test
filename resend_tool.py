# -*- coding: utf-8 -*-
"""
Outil de renvoi manuel pour la génération de projet.

Ce script permet de relancer une tâche de génération de projet et d'envoyer
le résultat à un webhook spécifié. C'est utile si l'envoi initial au webhook
a échoué (par exemple, si le webhook n'était pas actif).

Utilisation :
python resend_tool.py "description de votre projet" "https://votre.webhook.url/ici"
"""

import sys
import httpx
from fastapi_ssii.agents import project_manager

def resend_generation_to_webhook(description: str, webhook_url: str):
    """
    Génère le projet et envoie le résultat à l'URL du webhook.
    """
    if not description or not webhook_url:
        print("Erreur : La description et l'URL du webhook sont requises.")
        print(__doc__)
        sys.exit(1)

    print("="*50)
    print(f"Lancement de la régénération pour le projet : '{description}'")
    print("="*50)

    # Étape 1 : Génération du projet (nécessaire car le résultat n'est pas stocké)
    generation_result = project_manager.generate_project(description)

    if "error" in generation_result:
        print("\nUne erreur est survenue pendant la génération du projet.")
        print(generation_result)
        sys.exit(1)

    print("\n" + "="*50)
    print(f"Génération terminée. Envoi du résultat à : {webhook_url}")
    print("="*50)

    # Étape 2 : Envoi du résultat au webhook
    try:
        with httpx.Client() as client:
            response = client.post(
                webhook_url,
                json=generation_result,
                timeout=60.0  # Augmentation du timeout pour les grosses réponses
            )
            response.raise_for_status()

        print("\n🎉 Succès !")
        print(f"Résultat envoyé avec succès au webhook. Réponse du serveur : {response.status_code}")

    except httpx.RequestError as e:
        print(f"\n❌ Erreur réseau lors de l'envoi : {e}")
    except httpx.HTTPStatusError as e:
        print(f"\n❌ Erreur du serveur webhook : {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"\n❌ Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    # Récupérer les arguments depuis la ligne de commande
    if len(sys.argv) != 3:
        print("Erreur : Nombre d'arguments incorrect.")
        print(__doc__)
        sys.exit(1)

    project_description = sys.argv[1]
    target_webhook_url = sys.argv[2]

    resend_generation_to_webhook(project_description, target_webhook_url)
