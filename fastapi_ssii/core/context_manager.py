# fastapi_ssii/core/context_manager.py
from typing import Dict, List

class ContextManager:
    def __init__(self):
        self.entities: Dict[str, Dict] = {}
        self.relationships: Dict[str, List[str]] = {}
        self.api_endpoints: Dict[str, Dict] = {}
        self.database_schema: str = ""

    def register_entity(self, name: str, fields: Dict, relations: List):
        """Enregistre une entité pour qu'elle soit connue de tous les agents."""
        self.entities[name] = {
            'fields': fields,
            'relations': relations
        }

    def get_entity(self, name: str):
        """Récupère une entité pour assurer la cohérence."""
        return self.entities.get(name)

    def set_db_schema(self, schema: str):
        self.database_schema = schema

    def get_full_context(self) -> Dict:
        """Retourne un dictionnaire représentant le contexte global."""
        return {
            "entities": self.entities,
            "database_schema": self.database_schema,
            "api_endpoints": self.api_endpoints
        }

    def validate_consistency(self) -> List[str]:
        """Vérifie la cohérence entre tous les modules (simplifié)."""
        errors = []
        # Exemple de validation :
        # Pour chaque entité, vérifier qu'un modèle et un schéma correspondant existent.
        return errors
