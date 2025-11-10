from fastapi_ssii.agents import architect, backend_developer, frontend_developer, qa_engineer
from fastapi_ssii import project_store
import asyncio

async def generate_project(description: str) -> dict:
    """
    Orchestre la génération d'un projet de manière asynchrone et parallèle.
    """
    print("Étape 1 : Conception du projet par l'architecte (synchrone)...")
    # L'architecture doit être définie avant de pouvoir générer le code.
    project_plan = architect.design_project(description)

    if not project_plan.get("files") or "error.py" in project_plan["files"]:
        return {"error": "La génération du plan a échoué.", "plan": project_plan}

    print("Étape 2 : Lancement de la génération parallèle du code...")

    # Création des coroutines pour chaque groupe de tâches
    backend_task = backend_developer.generate_code(project_plan)
    frontend_task = frontend_developer.generate_code(project_plan)

    # Le QA doit attendre le code backend, donc il n'est pas dans le premier groupe.
    # On pourrait l'optimiser davantage, mais c'est un bon début.

    # Exécution des tâches de génération de code en parallèle
    results = await asyncio.gather(backend_task, frontend_task)

    backend_code = results[0]
    frontend_code = results[1]

    print("Étape 3 : Génération des tests (après le backend)...")
    # L'agent QA a besoin du code backend pour générer les tests.
    tests = await qa_engineer.generate_tests(project_plan, backend_code)

    print("Étape 4 : Assemblage final...")
    full_code = {**backend_code, **frontend_code, **tests}

    return {
        "message": "Projet généré avec succès !",
        "code": full_code,
        "plan": project_plan
    }

async def refine_project(project_id: str, feedback: str):
    """
    Orchestre le raffinement d'un projet (maintenant asynchrone).
    """
    print(f"Démarrage du raffinement pour {project_id}...")

    current_project = project_store.get_project(project_id)
    if not current_project:
        return

    # La logique de raffinement peut aussi être parallélisée si nécessaire
    refined_backend_code = await backend_developer.refine_code(
        plan=current_project["plan"],
        existing_code=current_project["code"],
        feedback=feedback
    )

    updated_code = {**current_project["code"], **refined_backend_code}
    project_store.update_project(project_id, {"code": updated_code, "status": "refined"})

    print(f"Raffinement du projet {project_id} terminé.")
    return project_store.get_project(project_id)
