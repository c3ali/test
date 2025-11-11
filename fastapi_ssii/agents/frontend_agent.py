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

        # Instructions spécifiques pour CSS
        css_instructions = ""
        if filename.endswith(".css"):
            css_instructions = """

RÈGLES CSS (IMPORTANT pour éviter les conflits):
- Utilise des sélecteurs spécifiques avec des classes préfixées
- Évite les sélecteurs globaux trop génériques (body, div, span, etc.)
- Préfère des classes BEM (Block Element Modifier) pour la nomenclature
- Exemple: .app-container, .board-card, .user-list__item
- Évite les !important sauf si absolument nécessaire
- Utilise des variables CSS pour les couleurs et tailles communes:
  :root {
    --primary-color: #4CAF50;
    --secondary-color: #2196F3;
    --background-color: #f5f5f5;
    --text-color: #333;
    --border-radius: 8px;
    --spacing: 16px;
  }
- Pour les interactions drag & drop, inclus ces classes utiles:
  .dragging { opacity: 0.5; cursor: grabbing; }
  .drag-over { border: 2px dashed var(--primary-color); background-color: rgba(76, 175, 80, 0.1); }
"""

        return f"""Génère le code {lang} complet et fonctionnel pour le fichier `{filename}`.

Description: {description}

IMPORTANT:
- Réponds UNIQUEMENT avec le code {lang} pur, sans aucun texte explicatif
- PAS de markdown (pas de ```, pas de ```{lang.lower()})
- PAS de commentaires explicatifs avant ou après le code
- PAS de description ou d'instructions
- Commence directement par le code
- Le code doit être complet et prêt à être utilisé{css_instructions}

Génère uniquement le contenu du fichier {lang}."""

    def _clean_code_response(self, code: str, file_ext: str) -> str:
        """
        Nettoie la réponse pour extraire uniquement le code valide.
        """
        # Détecter le type de balise markdown selon l'extension
        code_tags = []
        if file_ext == ".html":
            code_tags = ["```html", "```"]
        elif file_ext == ".css":
            code_tags = ["```css", "```"]
        elif file_ext in [".js", ".jsx", ".tsx"]:
            code_tags = ["```javascript", "```js", "```jsx", "```tsx", "```"]

        # Extraire le code des balises markdown
        for tag in code_tags:
            if tag in code:
                start = code.find(tag) + len(tag)
                end = code.find("```", start)
                if end != -1:
                    code = code[start:end]
                    break

        # Si pas de balises, essayer de nettoyer le texte markdown
        lines = code.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            # Ignorer les lignes de markdown claires
            if stripped.startswith(('###', '## ', '**Explanation', '**Note', '---', '```')):
                break
            cleaned_lines.append(line)

        code = '\n'.join(cleaned_lines).strip()

        # Supprimer les lignes vides excessives à la fin
        while code.endswith('\n\n\n'):
            code = code[:-1]

        return code

    async def _generate_file(self, filename: str, prompt: str) -> (str, str):
        logger.info(f"Génération du fichier frontend : {filename}")
        try:
            raw_response = await self.llm_client.generate_with_gemini_async(prompt)

            # Déterminer l'extension
            import os
            file_ext = os.path.splitext(filename)[1]

            # Nettoyage robuste du code
            code = self._clean_code_response(raw_response, file_ext)

            # Log pour débogage si le code semble contenir du markdown
            if '```' in code or '###' in code:
                print(f"[WARNING] Markdown détecté dans {filename} après nettoyage")

            return filename, code
        except Exception as e:
            logger.error(f"Erreur lors de la génération du fichier frontend : {filename}", error=str(e))
            raise

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        return []
