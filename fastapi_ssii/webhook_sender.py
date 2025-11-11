import httpx
from pydantic import HttpUrl
from fastapi_ssii.agents.project_manager import orchestrator
from fastapi_ssii import project_store, gemini_client
from fastapi_ssii.core.logger import get_logger
import asyncio
import re
from typing import Optional, Dict

logger = get_logger(__name__)


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
    logger.info(f"Démarrage de la génération pour le projet.", project_id=project_id)
    generation_result = await orchestrator.generate_project(description)

    if "error" in generation_result:
        project_store.update_project(project_id, {"status": "failed", "error": generation_result["error"]})
        logger.error("La génération du projet a échoué.", project_id=project_id, error=generation_result["error"])
        return

    project_store.save_generated_code(project_id, generation_result)

    repo_url = None
    if github_options:
        repo_name = github_options.get("repo_name")
        if not repo_name:
            logger.info("Aucun nom de dépôt fourni. Génération automatique...", project_id=project_id)
            repo_name = await generate_repo_name(description)
            logger.info(f"Nom de dépôt généré : {repo_name}", project_id=project_id)

        repo_url = await asyncio.to_thread(
            devops_agent.create_and_push_to_github,
            repo_name=repo_name,
            code_files=generation_result["code"],
            is_private=github_options.get("is_private", True)
        )
        project_store.update_project(project_id, {"github_url": repo_url})

    final_payload = { "project_id": project_id, "github_url": repo_url, **generation_result }

    if webhook_url:
        await send_to_webhook_async(webhook_url, final_payload)

    logger.info(f"Processus de génération pour le projet terminé.", project_id=project_id)


def generation_task(
    project_id: str,
    description: str,
    webhook_url: Optional[HttpUrl],
    github_options: Optional[Dict]
):
    asyncio.run(async_generation_task(project_id, description, webhook_url, github_options))

# ... (le reste du fichier)
