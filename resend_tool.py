# -*- coding: utf-8 -*-
"""
Outil de renvoi manuel pour la génération de projet.
... (docstring)
"""

import sys
import httpx
import asyncio
from fastapi_ssii.agents.project_manager import orchestrator

async def main(description: str, webhook_url: str):
    """
    Fonction principale asynchrone.
    """
    if not description or not webhook_url:
        print("Erreur : Description et URL du webhook sont requises.")
        sys.exit(1)

    print("="*50)
    print(f"Lancement de la régénération pour : '{description}'")
    print("="*50)

    # Étape 1 : Génération du projet avec le nouvel orchestrateur
    generation_result = await orchestrator.generate_project(description)

    if "error" in generation_result:
        print(f"\nErreur de génération : {generation_result['error']}")
        sys.exit(1)

    print("\n" + "="*50)
    print(f"Génération terminée. Envoi à : {webhook_url}")
    print("="*50)

    # Étape 2 : Envoi du résultat au webhook
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=generation_result, timeout=60.0)
            response.raise_for_status()

        print(f"\n🎉 Succès ! Réponse du serveur : {response.status_code}")

    except httpx.RequestError as e:
        print(f"\n❌ Erreur réseau : {e}")
    except httpx.HTTPStatusError as e:
        print(f"\n❌ Erreur du serveur webhook : {e.response.status_code} - {e.response.text}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Erreur : Nombre d'arguments incorrect.")
        sys.exit(1)

    project_description = sys.argv[1]
    target_webhook_url = sys.argv[2]

    # Lancer la coroutine principale
    asyncio.run(main(project_description, target_webhook_url))
