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
        Génère le code du backend en deux phases pour éviter les incohérences d'imports:
        Phase 1: Générer tous les modules utilitaires (models, middleware, etc.)
        Phase 2: Générer le fichier principal (main.py) avec le contexte des autres fichiers
        """
        plan = specification.get("plan", {})
        backend_files = {f: d for f, d in plan.get("files", {}).items() if f.endswith(".py") and not f.startswith("tests/")}

        # Séparer les fichiers en deux groupes
        main_files = ["main.py", "app.py", "server.py"]
        utility_files = {}
        entry_files = {}

        for filename, description in backend_files.items():
            if filename in main_files:
                entry_files[filename] = description
            else:
                utility_files[filename] = description

        # Phase 1: Générer les fichiers utilitaires en parallèle
        logger.info(f"Phase 1: Génération de {len(utility_files)} fichiers utilitaires")
        utility_tasks = []
        for filename, description in utility_files.items():
            prompt = self._build_prompt(filename, description, plan)
            utility_tasks.append(self._generate_file(filename, prompt))

        utility_results = await asyncio.gather(*utility_tasks) if utility_tasks else []
        generated_code = {filename: code for filename, code in utility_results}

        # Phase 2: Générer les fichiers d'entrée avec le contexte des utilitaires
        logger.info(f"Phase 2: Génération de {len(entry_files)} fichier(s) d'entrée avec contexte")
        entry_tasks = []
        for filename, description in entry_files.items():
            prompt = self._build_prompt(filename, description, plan, generated_code)
            entry_tasks.append(self._generate_file(filename, prompt))

        entry_results = await asyncio.gather(*entry_tasks) if entry_tasks else []
        for filename, code in entry_results:
            generated_code[filename] = code

        return generated_code

    def _build_prompt(self, filename: str, description: str, plan: Dict, generated_code: Dict[str, str] = None) -> str:
        """
        Construit le prompt pour la génération de code backend.
        Si generated_code est fourni, extrait les signatures de fonctions pour le contexte.
        """
        # Extraire la liste des fichiers du plan pour aider le LLM
        available_files = list(plan.get("files", {}).keys())
        files_info = "\n".join([f"- {f}" for f in available_files if f.endswith('.py')])

        # Si on a du code déjà généré, extraire les noms de fonctions/classes
        context_info = ""
        if generated_code:
            context_info = "\n\nCONTEXTE - Fonctions/Classes déjà définies dans les autres fichiers:\n"
            for gen_filename, gen_code in generated_code.items():
                # Extraire les définitions de fonctions et classes
                functions = self._extract_definitions(gen_code)
                if functions:
                    context_info += f"\n📁 {gen_filename}:\n"
                    for func_name in functions:
                        context_info += f"  - {func_name}\n"
            context_info += "\n⚠️ IMPORTANT: Utilise EXACTEMENT ces noms lors de l'import, PAS d'autres noms !\n"

        # Détecter si le projet a un frontend
        has_frontend = any(f.endswith((".html", ".css", ".js", ".vue", ".jsx", ".tsx"))
                          for f in available_files)

        # Ajouter des instructions spéciales pour le fichier principal si frontend détecté
        is_main_file = filename in ["main.py", "app.py", "server.py"]
        frontend_instructions = ""

        if has_frontend and is_main_file:
            frontend_instructions = """

SERVIR LE FRONTEND (TRÈS IMPORTANT):
- Ce projet a un frontend qui sera construit dans le dossier dist/
- Tu DOIS configurer FastAPI pour servir les fichiers statiques du frontend
- Ajoute ces imports en haut du fichier:
  from fastapi.staticfiles import StaticFiles
  from fastapi.responses import FileResponse
  import os

- Après la création de l'app FastAPI, ajoute:
  # Servir les fichiers statiques du frontend
  app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

- À la FIN du fichier (après toutes les routes API), ajoute cette route catch-all:
  @app.get("/{full_path:path}")
  async def serve_frontend(full_path: str):
      \"\"\"Serve the frontend for all non-API routes\"\"\"
      file_path = f"dist/{full_path}"
      if os.path.exists(file_path) and os.path.isfile(file_path):
          return FileResponse(file_path)
      # Fallback to index.html for SPA routing
      return FileResponse("dist/index.html")
"""

        return f"""Génère le code Python complet et fonctionnel pour le fichier `{filename}`.

Description: {description}

Fichiers Python disponibles dans le projet:
{files_info}{context_info}

IMPORTANT:
- Réponds UNIQUEMENT avec du code Python pur, sans aucun texte explicatif
- PAS de markdown (pas de ```, pas de ```python)
- PAS de commentaires explicatifs avant ou après le code
- PAS de description ou d'instructions
- Commence directement par les imports ou le code
- Le code doit être complet et prêt à être exécuté
- VÉRIFIE LA COHÉRENCE: Si tu importes une fonction, assure-toi qu'elle existe avec le même nom exact

IMPORTS ET STRUCTURE DE FICHIERS (TRÈS IMPORTANT):
- Les fichiers comme models.py, schemas.py, database.py sont des FICHIERS UNIQUES, PAS des packages/répertoires
- Même si le projet est dans un package (backend/, app/, etc.), ces fichiers restent des fichiers uniques

EXEMPLES D'IMPORTS CORRECTS:
✅ from models import User, Post, Board
✅ from schemas import UserCreate, UserResponse, BoardSchema
✅ from database import engine, SessionLocal, get_db
✅ from backend.models import User, Post (si backend/ est un package)
✅ from backend.schemas import UserSchema, BoardSchema (si backend/ est un package)
✅ from app.models import User (si app/ est un package)

EXEMPLES D'IMPORTS INCORRECTS:
❌ from models.user import User (models.user n'existe PAS - models.py est un fichier unique)
❌ from models.post import Post (models.post n'existe PAS)
❌ from schemas.board import BoardSchema (schemas.board n'existe PAS - schemas.py est un fichier unique)
❌ from backend.models.user import User (backend.models.user n'existe PAS)
❌ from backend.schemas.board import BoardSchema (backend.schemas.board n'existe PAS)
❌ from app.schemas.user import UserSchema (app.schemas.user n'existe PAS)

RÈGLE SIMPLE: N'ajoute JAMAIS de sous-module après models, schemas, database, etc.
- Si tu as besoin de User depuis models.py, utilise: from models import User ou from backend.models import User
- PAS from models.user ou from backend.models.user

TYPAGE PYTHON (IMPORTANT pour compatibilité Python 3.12/3.13):
- Pour SQLAlchemy avec Mapped, utilise TOUJOURS les types en minuscules (list, dict, set) au lieu de typing.List, typing.Dict, etc.
- Exemple CORRECT: Mapped[list["ClassName"]]
- Exemple INCORRECT: Mapped[List["ClassName"]]
- Pour les annotations de type normales (hors Mapped), tu peux utiliser list, dict, set directement
- N'importe pas List, Dict, Set depuis typing sauf si absolument nécessaire

CONVENTIONS DE NOMMAGE (CRITIQUE pour éviter les erreurs d'import):
Utilise TOUJOURS ces noms de fonctions standards pour assurer la cohérence:

📁 middleware/cors.py → fonction: setup_cors(app)
   Import dans main.py: from middleware.cors import setup_cors

📁 middleware/auth.py → fonction: setup_auth(app)
   Import dans main.py: from middleware.auth import setup_auth

📁 database.py → fonctions: get_db(), init_db()
   Import: from database import get_db, init_db

📁 config.py → classe: Settings (avec @property)
   Import: from config import Settings

📁 utils/*.py → noms descriptifs simples (get_*, create_*, validate_*)
   Exemple: utils/email.py → send_email(), validate_email()
   Import: from utils.email import send_email

RÈGLE D'OR: Si tu crées middleware/cors.py avec setup_cors, TOUS les imports doivent utiliser setup_cors, PAS add_cors_middleware ou autre nom !

Vérifie la cohérence:
1. Définis la fonction: def setup_cors(app): ...
2. Importe exactement le même nom: from middleware.cors import setup_cors
3. Appelle exactement le même nom: setup_cors(app){frontend_instructions}

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

    def _extract_definitions(self, code: str) -> List[str]:
        """
        Extrait les noms de fonctions et classes définies dans le code.
        """
        import re
        definitions = []

        # Extraire les classes
        class_pattern = r'^class\s+([A-Za-z_][A-Za-z0-9_]*)'
        for match in re.finditer(class_pattern, code, re.MULTILINE):
            definitions.append(f"class {match.group(1)}")

        # Extraire les fonctions (incluant async)
        func_pattern = r'^(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\('
        for match in re.finditer(func_pattern, code, re.MULTILINE):
            func_name = match.group(1)
            # Ignorer les méthodes privées et les méthodes magiques pour simplifier
            if not func_name.startswith('_'):
                definitions.append(f"def {func_name}()")

        return definitions

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        # La validation sera implémentée avec le CodeValidator
        return []
