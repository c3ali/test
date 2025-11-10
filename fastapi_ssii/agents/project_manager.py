from fastapi_ssii.agents import architect, backend_developer, frontend_developer, qa_engineer

def generate_project(description: str) -> dict:
    """
    Orchestre le processus de génération de projet en faisant appel
    séquentiellement aux agents spécialisés.
    """
    print("Étape 1 : Conception du projet par l'architecte...")
    project_plan = architect.design_project(description)

    # Si le plan a échoué, on arrête le processus
    if not project_plan.get("files") or "error.py" in project_plan["files"]:
        print("Erreur : L'architecte n'a pas pu générer un plan de projet valide.")
        return {"error": "La génération du plan a échoué.", "plan": project_plan}

    print("Étape 2 : Génération du code backend...")
    backend_code = backend_developer.generate_backend_code(project_plan)

    print("Étape 3 : Génération du code frontend...")
    frontend_code = frontend_developer.generate_frontend_code(project_plan)

    print("Étape 4 : Génération des tests par l'ingénieur QA...")
    # L'ingénieur QA a besoin du plan et du code backend pour écrire des tests pertinents
    tests = qa_engineer.generate_tests(project_plan, backend_code)

    print("Étape 5 : Assemblage final du code...")
    # Combinaison de tous les artefacts de code dans un seul dictionnaire
    full_code = {**backend_code, **frontend_code, **tests}

    # On pourrait aussi ajouter le plan et les dépendances à la réponse finale
    # pour plus de contexte.
    final_product = {
        "message": "Projet généré avec succès !",
        "code": full_code,
        "plan": project_plan
    }

    return final_product
