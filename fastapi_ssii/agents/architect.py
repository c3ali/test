import json
from fastapi_ssii import gemini_client

def design_project(description: str) -> dict:
    """
    Génère un plan de projet (structure de fichiers et dépendances)
    en utilisant l'API Gemini.

    Args:
        description: La description du projet fournie par l'utilisateur.

    Returns:
        Un dictionnaire contenant la structure de fichiers et les dépendances.
    """
    prompt = f"""
    En tant qu'architecte logiciel expert, conçois un plan pour un projet basé sur la description suivante : "{description}".

    Ta réponse DOIT être au format JSON et contenir deux clés :
    1. "files": un dictionnaire où chaque clé est un nom de fichier (ex: "main.py") et la valeur est une brève description de son rôle.
    2. "dependencies": une liste de chaînes de caractères représentant les bibliothèques Python nécessaires (ex: ["fastapi", "uvicorn"]).

    Exemple de réponse attendue :
    {{
      "files": {{
        "main.py": "Le point d'entrée de l'application FastAPI.",
        "models.py": "Les modèles de données Pydantic ou SQLAlchemy.",
        "views.py": "La logique des routes de l'API.",
        "tests/test_views.py": "Les tests pour les routes de l'API."
      }},
      "dependencies": ["fastapi", "uvicorn", "pytest"]
    }}

    Ne fournis que le JSON, sans aucun texte ou formatage supplémentaire.
    """

    response_text = gemini_client.generate_with_gemini(prompt)

    try:
        # Nettoyer la réponse pour s'assurer qu'elle est bien un JSON valide
        # Certains modèles могут retourner le JSON dans un bloc de code Markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:-4].strip()

        project_plan = json.loads(response_text)

        # Valider que les clés attendues sont présentes
        if "files" not in project_plan or "dependencies" not in project_plan:
            raise ValueError("La réponse JSON de Gemini ne contient pas les clés attendues.")

        return project_plan
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Erreur lors du parsing de la réponse de l'architecte : {e}")
        # Fournir un plan par défaut en cas d'échec
        return {
            "files": {"error.py": "Génération du plan échouée."},
            "dependencies": []
        }
