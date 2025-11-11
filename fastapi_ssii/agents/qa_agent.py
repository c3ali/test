from fastapi_ssii.agents.base_agent import BaseAgent
from fastapi_ssii.core.logger import get_logger
import asyncio
from typing import Dict, Any, List

logger = get_logger(__name__)

class QAAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("QAAgent", llm_client)
        self.add_dependency("BackendAgent")

    async def generate(self, specification: Dict[str, Any]) -> Dict[str, str]:
        """
        Génère les tests en parallèle.
        """
        plan = specification.get("plan", {})
        backend_code = specification.get("backend_code", {})
        test_files = [f for f in plan.get("files", {}).keys() if f.startswith("tests/")]

        tasks = []
        for test_filename in test_files:
            source_filename = test_filename.replace("tests/test_", "")
            source_code = backend_code.get(source_filename, "# Code source non trouvé.")
            prompt = self._build_prompt(test_filename, source_filename, source_code)
            tasks.append(self._generate_file(test_filename, prompt))

        logger.info(f"Lancement de la génération parallèle de {len(tasks)} fichiers de test.")
        generated_files = await asyncio.gather(*tasks)

        return {filename: code for filename, code in generated_files}

    def _build_prompt(self, test_filename: str, source_filename: str, source_code: str) -> str:
        return f"Écris les tests pytest pour `{test_filename}` afin de tester le fichier `{source_filename}`. Le code à tester est : ```python\n{source_code}```"

    async def _generate_file(self, filename: str, prompt: str) -> (str, str):
        logger.info(f"Génération du fichier de test : {filename}")
        try:
            code = await self.llm_client.generate_with_gemini_async(prompt)
            # Nettoyage des balises markdown
            if code.startswith("```python"):
                code = code[9:-4].strip()
            elif code.startswith("```"):
                lines = code.split('\n')
                code = '\n'.join(lines[1:-1]).strip()
            return filename, code
        except Exception as e:
            logger.error(f"Erreur lors de la génération du fichier de test : {filename}", error=str(e))
            raise

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        return []
