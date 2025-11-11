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
        logger.info("Génération du plan de projet.", description=description)

        prompt = f"""
        En tant qu'architecte logiciel expert, conçois un plan pour un projet basé sur la description suivante : "{description}".
        Ta réponse DOIT être un JSON valide contenant 'files' et 'dependencies'.
        """

        try:
            response_text = await self.llm_client.generate_with_gemini_async(prompt)
        except Exception as e:
            logger.error("Erreur lors de l'appel à l'API Gemini.", error=str(e))
            raise

        try:
            # Nettoyage de la réponse si elle contient des balises markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:-4].strip()
            elif response_text.startswith("```"):
                # Gérer le cas où il y a juste ``` sans "json"
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]).strip()

            project_plan = json.loads(response_text)
            self.validate_output(project_plan)
            return project_plan
        except json.JSONDecodeError as e:
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
