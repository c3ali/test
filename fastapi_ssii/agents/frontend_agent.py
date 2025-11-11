from fastapi_ssii.agents.base_agent import BaseAgent
from fastapi_ssii.core.logger import get_logger
import asyncio
from typing import Dict, Any, List

logger = get_logger(__name__)

class FrontendAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("FrontendAgent", llm_client)
        self.add_dependency("ArchitectAgent")

    async def generate(self, specification: Dict[str, Any]) -> Dict[str, str]:
        """
        Génère le code du frontend en parallèle.
        """
        plan = specification.get("plan", {})
        frontend_files = {f: d for f, d in plan.get("files", {}).items() if f.endswith((".html", ".css", ".js"))}

        tasks = []
        for filename, description in frontend_files.items():
            prompt = self._build_prompt(filename, description)
            tasks.append(self._generate_file(filename, prompt))

        logger.info(f"Lancement de la génération parallèle de {len(tasks)} fichiers frontend.")
        generated_files = await asyncio.gather(*tasks)

        return {filename: code for filename, code in generated_files}

    def _build_prompt(self, filename: str, description: str) -> str:
        lang = "HTML" if filename.endswith(".html") else "CSS" if filename.endswith(".css") else "JavaScript"
        return f"Écris le code {lang} pour le fichier `{filename}`. Description : {description}"

    async def _generate_file(self, filename: str, prompt: str) -> (str, str):
        logger.info(f"Génération du fichier frontend : {filename}")
        try:
            code = await self.llm_client.generate_with_gemini_async(prompt)
            # Nettoyage des balises markdown
            if code.startswith("```html") or code.startswith("```css") or code.startswith("```javascript") or code.startswith("```js"):
                lines = code.split('\n')
                code = '\n'.join(lines[1:-1]).strip()
            elif code.startswith("```"):
                lines = code.split('\n')
                code = '\n'.join(lines[1:-1]).strip()
            return filename, code
        except Exception as e:
            logger.error(f"Erreur lors de la génération du fichier frontend : {filename}", error=str(e))
            raise

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        return []
