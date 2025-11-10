import httpx
from pydantic import HttpUrl
from fastapi_ssii.agents import project_manager, devops_agent
from fastapi_ssii import project_store
import asyncio
from typing import Optional, Dict

def generation_task(
    project_id: str,
    description: str,
    webhook_url: Optional[HttpUrl],
    github_options: Optional[Dict]
):
    """
    Tâche de fond qui exécute la génération et potentiellement le push vers GitHub.
    """
    asyncio.run(async_generation_task(project_id, description, webhook_url, github_options))

async def async_generation_task(
    project_id: str,
    description: str,
    webhook_url: Optional[HttpUrl],
    github_options: Optional[Dict]
):
    print(f"Démarrage de la génération pour le projet ID : {project_id}")
    generation_result = await project_manager.generate_project(description)

    # S'il y a une erreur de génération, on arrête là.
    if "error" in generation_result:
        project_store.update_project(project_id, {"status": "failed", "error": generation_result["error"]})
        return

    project_store.save_generated_code(project_id, generation_result)

    # Si des options GitHub sont fournies, on appelle l'agent DevOps
    repo_url = None
    if github_options:
        print("Déploiement sur GitHub demandé...")
        repo_url = devops_agent.create_and_push_to_github(
            repo_name=github_options["repo_name"],
            code_files=generation_result["code"],
            is_private=github_options["is_private"]
        )
        project_store.update_project(project_id, {"github_url": repo_url})

    # Préparation de la réponse finale
    final_payload = {
        "project_id": project_id,
        "github_url": repo_url,
        **generation_result
    }

    if webhook_url:
        await send_to_webhook_async(webhook_url, final_payload)

    print(f"Processus de génération pour {project_id} terminé.")


# (Le reste du fichier reste le même pour le raffinement, qui n'intègre pas encore GitHub)
def refinement_task(project_id: str, feedback: str, webhook_url: HttpUrl):
    asyncio.run(async_refinement_task(project_id, feedback, webhook_url))

async def async_refinement_task(project_id: str, feedback: str, webhook_url: HttpUrl):
    refined_project = await project_manager.refine_project(project_id, feedback)
    webhook_payload = {"project_id": project_id, "refined_project": refined_project}
    if webhook_url:
        await send_to_webhook_async(webhook_url, webhook_payload)

async def send_to_webhook_async(webhook_url: HttpUrl, payload: dict):
    print(f"Envoi des données à {webhook_url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(str(webhook_url), json=payload, timeout=30.0)
            response.raise_for_status()
        print(f"Données envoyées avec succès. Statut : {response.status_code}")
    except httpx.RequestError as e:
        print(f"Erreur réseau : {e}")
    except httpx.HTTPStatusError as e:
        print(f"Erreur de statut HTTP : {e.response.status_code}")
