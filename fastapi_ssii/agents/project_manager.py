from fastapi_ssii.agents import architect, backend_developer, frontend_developer, qa_engineer
from fastapi_ssii import project_store

def generate_project(description: str) -> dict:
    """
    Orchestre la génération d'un NOUVEAU projet en appelant tous les agents.
    """
    print("Étape 1 : Conception du projet par l'architecte...")
    project_plan = architect.design_project(description)

    if not project_plan.get("files") or "error.py" in project_plan["files"]:
        return {"error": "La génération du plan a échoué.", "plan": project_plan}

    print("Étape 2 : Génération du code backend...")
    backend_code = backend_developer.generate_code(project_plan)

    print("Étape 3 : Génération du code frontend...")
    frontend_code = frontend_developer.generate_code(project_plan)

    print("Étape 4 : Génération des tests...")
    tests = qa_engineer.generate_tests(project_plan, backend_code)

    print("Étape 5 : Assemblage final...")
    full_code = {**backend_code, **frontend_code, **tests}

    return {
        "message": "Projet généré avec succès !",
        "code": full_code,
        "plan": project_plan
    }

def refine_project(project_id: str, feedback: str):
    """
    Orchestre le raffinement d'un projet EXISTANT.
    """
    print(f"Démarrage du raffinement pour le projet {project_id} avec le feedback : '{feedback}'")

    current_project = project_store.get_project(project_id)
    if not current_project:
        print(f"Erreur : Projet {project_id} non trouvé pour le raffinement.")
        return

    current_plan = current_project["plan"]
    current_code = current_project["code"]

    print("Étape 2 (Raffinement) : Amélioration du code backend...")
    refined_backend_code = backend_developer.refine_code(
        plan=current_plan,
        existing_code=current_code,
        feedback=feedback
    )

    updated_code = {**current_code, **refined_backend_code}

    project_store.update_project(project_id, {"code": updated_code, "status": "refined"})

    print(f"Raffinement du projet {project_id} terminé.")

    return project_store.get_project(project_id)
