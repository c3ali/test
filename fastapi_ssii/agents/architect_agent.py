from fastapi_ssii.agents.base_agent import BaseAgent
from fastapi_ssii.core.logger import get_logger
import json
from typing import Dict, Any, List

logger = get_logger(__name__)

class ArchitectAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("ArchitectAgent", llm_client)

    async def generate(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        description = specification.get("description", "")
        tech_spec = specification.get("tech_spec", {})
        logger.info("Génération du plan de projet.", description=description)

        prompt = f"""En tant qu'architecte logiciel expert, conçois un plan technique pour le projet suivant:

Description: "{description}"

Spécifications techniques:
- Résumé: {tech_spec.get('project_summary', 'N/A')}
- Fonctionnalités: {', '.join(tech_spec.get('main_features', []))}
- Entités de données: {', '.join([e['name'] for e in tech_spec.get('data_entities', [])])}

IMPORTANT: Ta réponse doit contenir UNIQUEMENT un JSON valide, sans texte explicatif avant ou après, et sans balises markdown.

Le JSON doit contenir exactement ces clés:
- files: Un dictionnaire où chaque clé est un nom de fichier et chaque valeur est une description de ce que le fichier doit contenir (dict)
- dependencies: Une liste des dépendances externes nécessaires (array of strings)

Exemple de format:
{{
  "files": {{
    "main.py": "Point d'entrée de l'application FastAPI avec les routes",
    "models.py": "Modèles de données SQLAlchemy",
    "database.py": "Configuration de la base de données"
  }},
  "dependencies": ["fastapi", "uvicorn", "sqlalchemy"]
}}

Réponds uniquement avec le JSON, commence directement par {{ et termine par }}."""

        try:
            response_text = await self.llm_client.generate_with_gemini_async(prompt)
        except Exception as e:
            logger.error("Erreur lors de l'appel à l'API Gemini.", error=str(e))
            raise

        try:
            # Nettoyage de la réponse si elle contient des balises markdown
            original_response = response_text
            if response_text.startswith("```json"):
                response_text = response_text[7:-4].strip()
            elif response_text.startswith("```"):
                # Gérer le cas où il y a juste ``` sans "json"
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]).strip()

            # Essayer de trouver le JSON s'il est entouré de texte
            if not response_text.startswith('{'):
                start_idx = response_text.find('{')
                if start_idx != -1:
                    response_text = response_text[start_idx:]

            if not response_text.endswith('}'):
                end_idx = response_text.rfind('}')
                if end_idx != -1:
                    response_text = response_text[:end_idx + 1]

            project_plan = json.loads(response_text)
            self.validate_output(project_plan)
            return project_plan
        except json.JSONDecodeError as e:
            # Logging explicite pour Railway
            print(f"[DEBUG] Architect JSON Error: {e}")
            print(f"[DEBUG] Original response (first 500 chars): {original_response[:500]}")
            print(f"[DEBUG] Cleaned response (first 500 chars): {response_text[:500]}")
            logger.error("Échec du parsing JSON du plan de l'architecte.",
                        error=str(e),
                        response_preview=response_text[:500])
            raise
        except ValueError as e:
            logger.error("Échec de la validation du plan de l'architecte.", error=str(e))
            raise

    def validate_output(self, output: Dict[str, Any]) -> List[str]:
        errors = []
        if "files" not in output or not isinstance(output["files"], dict):
            errors.append("La clé 'files' est manquante ou n'est pas un dictionnaire.")
        if "dependencies" not in output or not isinstance(output["dependencies"], list):
            errors.append("La clé 'dependencies' est manquante ou n'est pas une liste.")

        if errors:
            raise ValueError(f"Validation du plan échouée : {', '.join(errors)}")
        return []
