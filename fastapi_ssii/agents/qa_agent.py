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
        return f"""Génère les tests pytest complets pour `{test_filename}` afin de tester le fichier `{source_filename}`.

Code à tester:
{source_code}

IMPORTANT:
- Réponds UNIQUEMENT avec du code Python de test pytest, sans aucun texte explicatif
- PAS de markdown (pas de ```, pas de ```python)
- PAS de commentaires explicatifs avant ou après le code
- PAS de description ou d'instructions
- Commence directement par les imports
- Les tests doivent être complets et prêts à être exécutés

Génère uniquement le contenu du fichier de test Python."""

    def _clean_code_response(self, code: str) -> str:
        """
        Nettoie la réponse pour extraire uniquement le code de test Python valide.
        """
        # 1. Enlever les balises markdown
        if "```python" in code:
            start = code.find("```python") + 9
            end = code.find("```", start)
            if end != -1:
                code = code[start:end]
        elif code.startswith("```"):
            lines = code.split('\n')
            start_idx = 1
            end_idx = len(lines)
            for i in range(len(lines) - 1, 0, -1):
                if lines[i].strip() == "```":
                    end_idx = i
                    break
            code = '\n'.join(lines[start_idx:end_idx])

        # 2. Supprimer le texte markdown/explicatif
        lines = code.split('\n')
        cleaned_lines = []
        in_code = False

        for line in lines:
            stripped = line.strip()

            # Détecter le début du code Python
            if not in_code and (
                stripped.startswith(('import ', 'from ', 'def ', 'class ', 'async def', '@', '#'))
                or (stripped and not stripped.startswith(('###', '**', '##', '-', '*', '>', 'Note:')))):
                in_code = True

            # Si on est dans le code, ajouter la ligne
            if in_code:
                # Arrêter si on détecte du markdown clair
                if stripped.startswith(('###', '## ', '**Explanation', '**Note', '---', '```')):
                    break
                cleaned_lines.append(line)

        code = '\n'.join(cleaned_lines).strip()

        # 3. Supprimer les lignes vides excessives à la fin
        while code.endswith('\n\n\n'):
            code = code[:-1]

        return code

    async def _generate_file(self, filename: str, prompt: str) -> (str, str):
        logger.info(f"Génération du fichier de test : {filename}")
        try:
            raw_response = await self.llm_client.generate_with_gemini_async(prompt)

            # Nettoyage robuste du code
            code = self._clean_code_response(raw_response)

            # Log pour débogage si le code semble contenir du markdown
            if '```' in code or '###' in code or '**' in code:
                print(f"[WARNING] Markdown détecté dans {filename} après nettoyage")

            return filename, code
        except Exception as e:
            logger.error(f"Erreur lors de la génération du fichier de test : {filename}", error=str(e))
            raise

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        return []
