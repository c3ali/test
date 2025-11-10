import httpx
from pydantic import HttpUrl
from fastapi_ssii.agents import project_manager
from fastapi_ssii import project_store
import asyncio

def generation_task(project_id: str, description: str, webhook_url: HttpUrl):
    """
    Tâche de fond (synchrone) qui lance l'exécution de la coroutine de génération.
    """
    asyncio.run(async_generation_task(project_id, description, webhook_url))

async def async_generation_task(project_id: str, description: str, webhook_url: HttpUrl):
    print(f"Démarrage de la tâche de génération pour le projet ID : {project_id}")
    generation_result = await project_manager.generate_project(description)
    project_store.save_generated_code(project_id, generation_result)

    webhook_payload = {"project_id": project_id, **generation_result}

    if webhook_url:
        await send_to_webhook_async(webhook_url, webhook_payload)

def refinement_task(project_id: str, feedback: str, webhook_url: HttpUrl):
    """
    Tâche de fond (synchrone) qui lance l'exécution de la coroutine de raffinement.
    """
    asyncio.run(async_refinement_task(project_id, feedback, webhook_url))

async def async_refinement_task(project_id: str, feedback: str, webhook_url: HttpUrl):
    print(f"Démarrage de la tâche de raffinement pour le projet ID : {project_id}")
    refined_project = await project_manager.refine_project(project_id, feedback)
    webhook_payload = {"project_id": project_id, "refined_project": refined_project}

    if webhook_url:
        await send_to_webhook_async(webhook_url, webhook_payload)

async def send_to_webhook_async(webhook_url: HttpUrl, payload: dict):
    """
    Fonction utilitaire pour envoyer des données à un webhook de manière asynchrone.
    """
    print(f"Envoi des données à {webhook_url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(str(webhook_url), json=payload, timeout=30.0)
            response.raise_for_status()
        print(f"Données envoyées avec succès. Statut : {response.status_code}")
    except httpx.RequestError as e:
        print(f"Erreur réseau lors de l'envoi au webhook : {e}")
    except httpx.HTTPStatusError as e:
        print(f"Erreur de statut HTTP : {e.response.status_code} - {e.response.text}")
