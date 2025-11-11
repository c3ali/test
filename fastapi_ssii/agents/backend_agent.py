from fastapi_ssii.agents.base_agent import BaseAgent
from fastapi_ssii.core.logger import get_logger
import asyncio
from typing import Dict, Any, List

logger = get_logger(__name__)

class BackendAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("BackendAgent", llm_client)
        self.add_dependency("ArchitectAgent")

    async def generate(self, specification: Dict[str, Any]) -> Dict[str, str]:
        """
        Génère le code du backend en parallèle pour chaque fichier pertinent du plan.
        """
        plan = specification.get("plan", {})
        backend_files = {f: d for f, d in plan.get("files", {}).items() if f.endswith(".py") and not f.startswith("tests/")}

        tasks = []
        for filename, description in backend_files.items():
            prompt = self._build_prompt(filename, description, plan)
            tasks.append(self._generate_file(filename, prompt))

        logger.info(f"Lancement de la génération parallèle de {len(tasks)} fichiers backend.")
        generated_files = await asyncio.gather(*tasks)

        return {filename: code for filename, code in generated_files}

    def _build_prompt(self, filename: str, description: str, plan: Dict) -> str:
        # La logique de construction du prompt est maintenant isolée.
        # Plus tard, elle sera remplacée par le PromptBuilder.
        return f"Écris le code Python pour le fichier `{filename}`. Description : {description}"

    async def _generate_file(self, filename: str, prompt: str) -> (str, str):
        logger.info(f"Génération du fichier backend : {filename}")
        code = await self.llm_client.generate_with_gemini_async(prompt)
        if code.startswith("```python"):
            code = code[9:-4].strip()
        return filename, code

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        # La validation sera implémentée avec le CodeValidator
        return []
