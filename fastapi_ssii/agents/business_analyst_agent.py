from fastapi_ssii.agents.base_agent import BaseAgent
from fastapi_ssii.core.logger import get_logger
import json
from typing import Dict, Any, List

logger = get_logger(__name__)

class BusinessAnalystAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("BusinessAnalystAgent", llm_client)

    async def generate(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse la description brute et la transforme en spécification technique.
        """
        description = specification.get("description", "")
        logger.info("Analyse de la demande client...", description=description)

        prompt = self._build_prompt(description)

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
                # Chercher le début du JSON
                start_idx = response_text.find('{')
                if start_idx != -1:
                    response_text = response_text[start_idx:]

            if not response_text.endswith('}'):
                # Chercher la fin du JSON
                end_idx = response_text.rfind('}')
                if end_idx != -1:
                    response_text = response_text[:end_idx + 1]

            tech_spec = json.loads(response_text)
            self.validate_output(tech_spec)
            return tech_spec
        except json.JSONDecodeError as e:
            # Logging explicite pour Railway
            print(f"[DEBUG] Business Analyst JSON Error: {e}")
            print(f"[DEBUG] Original response (first 500 chars): {original_response[:500]}")
            print(f"[DEBUG] Cleaned response (first 500 chars): {response_text[:500]}")
            logger.error("Échec du parsing JSON de la spécification technique.",
                        error=str(e),
                        response_preview=response_text[:500])
            raise
        except ValueError as e:
            logger.error("Échec de la validation de la spécification technique.", error=str(e))
            raise

    def _build_prompt(self, description: str) -> str:
        return f"""En tant qu'analyste métier (Business Analyst) expert, transforme la demande brute suivante en une spécification technique structurée au format JSON.

Demande du client : "{description}"

IMPORTANT: Ta réponse doit contenir UNIQUEMENT le JSON valide, sans aucun texte explicatif avant ou après, et sans balises markdown.

Le JSON doit contenir exactement ces clés:
- project_summary: Un résumé clair et concis du projet (string)
- main_features: Une liste de 3 à 5 fonctionnalités principales (array of strings)
- data_entities: Une liste d'entités de données, chaque entité ayant un "name" et une liste de "fields" (array of objects)

Exemple de format attendu:
{{
  "project_summary": "Une API RESTful pour un système de blog simple",
  "main_features": [
    "Création de nouveaux articles",
    "Lecture de la liste des articles",
    "Gestion des utilisateurs"
  ],
  "data_entities": [
    {{"name": "User", "fields": ["id", "username", "email", "password_hash"]}},
    {{"name": "Post", "fields": ["id", "title", "content", "author_id", "created_at"]}}
  ]
}}

Réponds uniquement avec le JSON, commence directement par {{ et termine par }}."""

    def validate_output(self, output: Dict[str, Any]) -> List[str]:
        errors = []
        required_keys = ["project_summary", "main_features", "data_entities"]
        for key in required_keys:
            if key not in output:
                errors.append(f"La clé requise '{key}' est manquante dans la spécification.")

        if errors:
            raise ValueError(f"Validation de la spécification échouée : {', '.join(errors)}")
        return []
