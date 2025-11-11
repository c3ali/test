import httpx
from pydantic import HttpUrl
from fastapi_ssii.agents import project_manager, devops_agent
from fastapi_ssii import project_store, gemini_client
import asyncio
import re
from typing import Optional, Dict

async def generate_repo_name(description: str) -> str:
    """
    Génère un nom de dépôt pertinent à partir de la description.
    """
    prompt = f"""
    Basé sur la description de projet suivante, propose un nom de dépôt GitHub court et pertinent.
    Description : "{description}"
    Le nom doit être en minuscules, utiliser le format kebab-case (mots séparés par des tirets), et ne contenir que des lettres, des chiffres ou des tirets.
    Ta réponse doit contenir UNIQUEMENT le nom du dépôt.
    Exemple de réponse : "simple-blog-api"
    """
    repo_name = await gemini_client.generate_with_gemini_async(prompt)
    # Nettoyage simple pour s'assurer du format
    repo_name = re.sub(r'[^a-z0-9-]+', '-', repo_name.lower()).strip('-')
    return repo_name

async def async_generation_task(
    project_id: str,
    description: str,
    webhook_url: Optional[HttpUrl],
    github_options: Optional[Dict]
):
    print(f"Démarrage de la génération pour le projet ID : {project_id}")
    generation_result = await project_manager.generate_project(description)

    if "error" in generation_result:
        project_store.update_project(project_id, {"status": "failed", "error": generation_result["error"]})
        return

    project_store.save_generated_code(project_id, generation_result)

    repo_url = None
    if github_options:
        repo_name = github_options.get("repo_name")
        if not repo_name:
            print("Aucun nom de dépôt fourni. Génération automatique...")
            repo_name = await generate_repo_name(description)
            print(f"Nom de dépôt généré : {repo_name}")

        repo_url = await asyncio.to_thread(
            devops_agent.create_and_push_to_github,
            repo_name=repo_name,
            code_files=generation_result["code"],
            is_private=github_options.get("is_private", True)
        )
        project_store.update_project(project_id, {"github_url": repo_url})

    final_payload = {
        "project_id": project_id,
        "github_url": repo_url,
        **generation_result
    }

    if webhook_url:
        await send_to_webhook_async(webhook_url, final_payload)

    print(f"Processus de génération pour {project_id} terminé.")

# (Le reste du fichier reste identique)
def generation_task(
    project_id: str,
    description: str,
    webhook_url: Optional[HttpUrl],
    github_options: Optional[Dict]
):
    asyncio.run(async_generation_task(project_id, description, webhook_url, github_options))
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
