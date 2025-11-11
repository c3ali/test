import httpx
from pydantic import HttpUrl
from fastapi_ssii.agents.project_manager import orchestrator
from fastapi_ssii.agents.devops_agent import DevOpsAgent
from fastapi_ssii import project_store, gemini_client
from fastapi_ssii.core.logger import get_logger
import asyncio
import re
from typing import Optional, Dict

logger = get_logger(__name__)
devops_agent = DevOpsAgent()


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


async def send_to_webhook_async(webhook_url: HttpUrl, payload: Dict):
    """
    Envoie un payload à une URL de webhook de manière asynchrone.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(str(webhook_url), json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Webhook appelé avec succès : {webhook_url}")
    except httpx.HTTPError as e:
        logger.error(f"Erreur lors de l'appel du webhook : {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'appel du webhook : {e}")


async def async_refinement_task(
    project_id: str,
    feedback: str,
    webhook_url: Optional[HttpUrl]
):
    """
    Tâche asynchrone de raffinement d'un projet basé sur le feedback.
    """
    logger.info(f"Démarrage du raffinement pour le projet.", project_id=project_id)

    project = project_store.get_project(project_id)
    if not project:
        logger.error(f"Projet non trouvé pour le raffinement.", project_id=project_id)
        return

    # Mettre à jour le statut du projet
    project_store.update_project(project_id, {"status": "refining"})

    # Pour le moment, on régénère le projet avec la description enrichie du feedback
    # Dans une version plus avancée, on pourrait avoir une méthode spécifique de raffinement
    enhanced_description = f"{project.get('description', '')} \n\nFeedback pour amélioration: {feedback}"

    refinement_result = await orchestrator.generate_project(enhanced_description)

    if "error" in refinement_result:
        project_store.update_project(project_id, {"status": "failed", "error": refinement_result["error"]})
        logger.error("Le raffinement du projet a échoué.", project_id=project_id, error=refinement_result["error"])
        return

    project_store.save_generated_code(project_id, refinement_result)

    final_payload = {
        "project_id": project_id,
        "status": "refined",
        **refinement_result
    }

    if webhook_url:
        await send_to_webhook_async(webhook_url, final_payload)

    logger.info(f"Processus de raffinement pour le projet terminé.", project_id=project_id)


def refinement_task(
    project_id: str,
    feedback: str,
    webhook_url: Optional[HttpUrl]
):
    """
    Tâche synchrone de raffinement pour être utilisée avec BackgroundTasks.
    """
    asyncio.run(async_refinement_task(project_id, feedback, webhook_url))
