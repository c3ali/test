# fastapi_ssii/project_store.py
import uuid
from typing import Dict, Any

# --- Stockage en mémoire ---
# C'est une base de données "en mémoire" très simple.
# Elle sera réinitialisée à chaque redémarrage du serveur.
# La clé est le project_id, la valeur est le dictionnaire du projet.
_project_database: Dict[str, Dict[str, Any]] = {}

def create_new_project(description: str) -> str:
    """
    Crée une nouvelle entrée pour un projet et retourne son ID unique.
    """
    project_id = str(uuid.uuid4())
    _project_database[project_id] = {
        "id": project_id,
        "description": description,
        "status": "pending",
        "code": {},
        "plan": {}
    }
    print(f"Projet créé avec l'ID : {project_id}")
    return project_id

def get_project(project_id: str) -> Dict[str, Any]:
    """
    Récupère un projet par son ID.
    """
    return _project_database.get(project_id)

def update_project(project_id: str, data: Dict[str, Any]):
    """
    Met à jour un projet avec de nouvelles données (par exemple, le code généré).
    """
    if project_id in _project_database:
        _project_database[project_id].update(data)
        print(f"Projet {project_id} mis à jour.")
    else:
        print(f"Tentative de mise à jour d'un projet inexistant : {project_id}")

def save_generated_code(project_id: str, generation_result: Dict[str, Any]):
    """
    Une fonction utilitaire pour sauvegarder le résultat complet de la génération.
    """
    update_data = {
        "status": "completed",
        "code": generation_result.get("code", {}),
        "plan": generation_result.get("plan", {})
    }
    update_project(project_id, update_data)
