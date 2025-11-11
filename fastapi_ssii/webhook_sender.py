# ... (imports)
from fastapi_ssii.agents.project_manager import orchestrator

# ... (autres fonctions)

async def async_generation_task(
    project_id: str,
    description: str,
    webhook_url: Optional[HttpUrl],
    github_options: Optional[Dict]
):
    logger.info(f"Démarrage de la génération pour le projet.", project_id=project_id)

    # Utilisation de l'instance de l'orchestrateur
    generation_result = await orchestrator.generate_project(description)

    # ... (le reste de la logique reste identique)

    if "error" in generation_result:
        # ...
        return

    project_store.save_generated_code(project_id, generation_result)

    repo_url = None
    if github_options:
        # ...
        project_store.update_project(project_id, {"github_url": repo_url})

    final_payload = { "project_id": project_id, "github_url": repo_url, **generation_result }

    if webhook_url:
        await send_to_webhook_async(webhook_url, final_payload)

    logger.info(f"Processus de génération terminé.", project_id=project_id)

# ... (le reste du fichier)
