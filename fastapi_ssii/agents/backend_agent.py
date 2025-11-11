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
        """
        Construit le prompt pour la génération de code backend.
        """
        # Extraire la liste des fichiers du plan pour aider le LLM
        available_files = list(plan.get("files", {}).keys())
        files_info = "\n".join([f"- {f}" for f in available_files if f.endswith('.py')])

        return f"""Génère le code Python complet et fonctionnel pour le fichier `{filename}`.

Description: {description}

Fichiers Python disponibles dans le projet:
{files_info}

IMPORTANT:
- Réponds UNIQUEMENT avec du code Python pur, sans aucun texte explicatif
- PAS de markdown (pas de ```, pas de ```python)
- PAS de commentaires explicatifs avant ou après le code
- PAS de description ou d'instructions
- Commence directement par les imports ou le code
- Le code doit être complet et prêt à être exécuté

IMPORTS ET STRUCTURE DE FICHIERS (TRÈS IMPORTANT):
- Les fichiers comme models.py, schemas.py, database.py sont des FICHIERS UNIQUES, pas des packages
- CORRECT: from models import User, Post
- CORRECT: from database import engine, SessionLocal
- INCORRECT: from models.user import User (models n'est PAS un package)
- INCORRECT: from models.post import Post (models n'est PAS un package)
- Si le fichier est dans un sous-dossier (ex: routers/users.py), utilise des imports relatifs ou absolus corrects
- Exemple pour routers/users.py: from models import User OU from ..models import User
- NE crée PAS d'imports vers des sous-modules qui n'existent pas

TYPAGE PYTHON (IMPORTANT pour compatibilité Python 3.12/3.13):
- Pour SQLAlchemy avec Mapped, utilise TOUJOURS les types en minuscules (list, dict, set) au lieu de typing.List, typing.Dict, etc.
- Exemple CORRECT: Mapped[list["ClassName"]]
- Exemple INCORRECT: Mapped[List["ClassName"]]
- Pour les annotations de type normales (hors Mapped), tu peux utiliser list, dict, set directement
- N'importe pas List, Dict, Set depuis typing sauf si absolument nécessaire

Génère uniquement le contenu du fichier Python."""

    def _clean_code_response(self, code: str) -> str:
        """
        Nettoie la réponse pour extraire uniquement le code Python valide.
        """
        # 1. Enlever les balises markdown au début et à la fin
        if "```python" in code:
            # Extraire le code entre ```python et ```
            start = code.find("```python") + 9
            end = code.find("```", start)
            if end != -1:
                code = code[start:end]
        elif code.startswith("```"):
            # Gérer les balises ``` sans python
            lines = code.split('\n')
            # Trouver la première ligne après ```
            start_idx = 1
            # Trouver la dernière ligne avant ```
            end_idx = len(lines)
            for i in range(len(lines) - 1, 0, -1):
                if lines[i].strip() == "```":
                    end_idx = i
                    break
            code = '\n'.join(lines[start_idx:end_idx])

        # 2. Supprimer le texte markdown/explicatif après le code
        # Détecter les patterns de texte explicatif
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
                # Arrêter si ligne de texte explicatif après code vide
                if not stripped and len(cleaned_lines) > 0:
                    # Vérifier si les prochaines lignes sont du markdown
                    continue
                cleaned_lines.append(line)

        code = '\n'.join(cleaned_lines).strip()

        # 3. Supprimer les lignes vides excessives à la fin
        while code.endswith('\n\n\n'):
            code = code[:-1]

        return code

    async def _generate_file(self, filename: str, prompt: str) -> (str, str):
        logger.info(f"Génération du fichier backend : {filename}")
        try:
            raw_response = await self.llm_client.generate_with_gemini_async(prompt)

            # Nettoyage robuste du code
            code = self._clean_code_response(raw_response)

            # Log pour débogage si le code semble contenir du markdown
            if '```' in code or '###' in code or '**' in code:
                print(f"[WARNING] Markdown détecté dans {filename} après nettoyage")
                print(f"[DEBUG] Code preview: {code[:200]}")

            return filename, code
        except Exception as e:
            logger.error(f"Erreur lors de la génération du fichier backend : {filename}", error=str(e))
            raise

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        # La validation sera implémentée avec le CodeValidator
        return []
