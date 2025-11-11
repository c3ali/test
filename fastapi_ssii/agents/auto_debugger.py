from fastapi_ssii.core.logger import get_logger
from fastapi_ssii.agents.learning_agent import LearningAgent
import httpx
import re
import asyncio
from typing import Dict, List, Tuple, Any, Optional

logger = get_logger(__name__)

class AutoDebugger:
    """
    Agent autonome pour détecter et corriger automatiquement les bugs
    lors du déploiement.

    Intégré avec LearningAgent pour apprendre des erreurs et améliorer
    continuellement le code généré.
    """

    def __init__(self, llm_client, deployment_agent, learning_agent: Optional[LearningAgent] = None):
        self.llm_client = llm_client
        self.deployment_agent = deployment_agent
        self.learning_agent = learning_agent or LearningAgent(llm_client)

    async def deploy_with_auto_fix(
        self,
        code_files: Dict[str, str],
        specification: Dict[str, Any]
    ) -> Tuple[bool, Dict]:
        """
        Déploie et corrige automatiquement les bugs jusqu'à réussite.

        Utilise le LearningAgent pour apprendre des erreurs et adapter
        intelligemment le nombre d'itérations (pas de limite fixe).

        Returns:
            (success: bool, result: dict)
        """
        iteration = 0
        deployment_success = False
        logs_history = []
        current_code = code_files.copy()

        logger.info(f"🚀 Début du déploiement avec auto-correction intelligente (apprentissage activé)")

        while not deployment_success and self.learning_agent.should_continue_iterations(iteration):
            iteration += 1
            logger.info(f"🔄 Itération {iteration} (apprentissage actif)")

            # 1. Tenter le déploiement
            deployment_result = await self.deployment_agent.generate(specification)

            # 2. Vérifier si le déploiement a réussi
            if "error" not in deployment_result:
                # Tester l'application déployée
                deployment_url = deployment_result.get("deployment", {}).get("url")

                if deployment_url:
                    health = await self.check_application_health(deployment_url)

                    if health["healthy"]:
                        deployment_success = True
                        logger.info("✅ Déploiement réussi!")
                        break
                    else:
                        # Bugs runtime détectés
                        error_list = health.get("errors", [])
                        logger.info(f"⚠️ {len(error_list)} erreurs détectées")

                        # Convertir les erreurs en format bugs pour analyse
                        bugs = []
                        for error in error_list:
                            bugs.append({
                                "type": "runtime_error",
                                "error": error,
                                "file": "N/A"
                            })
                else:
                    # Pas d'URL, mais pas d'erreur non plus (création projet seulement)
                    deployment_success = True
                    logger.info("✅ Projet créé avec succès")
                    break

            else:
                # Erreur de déploiement
                error_msg = deployment_result.get("error", "Unknown error")
                logger.error(f"❌ Erreur de déploiement: {error_msg}")

                bugs = await self.analyze_deployment_error(error_msg)

            # 3. Apprentissage et correction des bugs détectés
            if bugs:
                logger.info(f"🔧 Correction de {len(bugs)} bugs...")

                # Apprendre de chaque erreur
                for bug in bugs:
                    error_type = bug.get("type", "UnknownError")
                    error_message = bug.get("error", str(bug))

                    learning_result = await self.learning_agent.learn_from_error(
                        error_type=error_type,
                        error_message=error_message,
                        context={
                            "agent": "AutoDebugger",
                            "file": bug.get("file", "N/A"),
                            "bug_details": bug
                        },
                        iteration=iteration
                    )

                    if learning_result.get("action") == "permanent_improvement":
                        logger.info(f"🎓 Amélioration permanente générée pour {learning_result.get('agent')}")

                # Corriger le code
                current_code = await self.fix_bugs(current_code, bugs)

                # Mettre à jour le code dans la spécification
                specification["code_files"] = current_code

                logs_history.append({
                    "iteration": iteration,
                    "bugs_found": len(bugs),
                    "bugs": bugs,
                    "learning_result": learning_result if 'learning_result' in locals() else None
                })

        # Obtenir les statistiques d'apprentissage
        learning_stats = self.learning_agent.get_learning_stats()

        return deployment_success, {
            "code": current_code,
            "iterations": iteration,
            "logs": logs_history,
            "deployment": deployment_result if 'deployment_result' in locals() else {},
            "learning_stats": learning_stats
        }

    async def check_application_health(self, url: str) -> Dict:
        """Vérifie la santé de l'application déployée"""

        checks = {
            "healthy": True,
            "errors": []
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test endpoint racine
                try:
                    response = await client.get(url)
                    if response.status_code >= 500:
                        checks["healthy"] = False
                        checks["errors"].append(f"Server error: {response.status_code}")
                except httpx.TimeoutException:
                    checks["healthy"] = False
                    checks["errors"].append("Application timeout")
                except Exception as e:
                    checks["healthy"] = False
                    checks["errors"].append(f"Connection error: {str(e)}")

        except Exception as e:
            checks["healthy"] = False
            checks["errors"].append(f"Health check failed: {str(e)}")

        return checks

    async def analyze_deployment_error(self, error_msg: str) -> List[Dict]:
        """Analyse le message d'erreur pour identifier les bugs"""

        bugs = []

        # Pattern: Module manquant
        missing_modules = re.findall(r"ModuleNotFoundError: No module named '([^']+)'", error_msg)
        for module in missing_modules:
            bugs.append({
                "type": "missing_dependency",
                "module": module,
                "file": "requirements.txt"
            })

        # Pattern: Erreur de syntaxe
        syntax_errors = re.findall(
            r'File "([^"]+)", line (\d+).*\n.*?(\w+Error: .+)',
            error_msg
        )
        for file, line, error in syntax_errors:
            bugs.append({
                "type": "syntax_error",
                "file": file,
                "line": int(line),
                "error": error
            })

        # Pattern: Import error
        import_errors = re.findall(
            r"ImportError: cannot import name '([^']+)' from '([^']+)'",
            error_msg
        )
        for name, module in import_errors:
            bugs.append({
                "type": "import_error",
                "name": name,
                "module": module
            })

        # Pattern: Erreur de base de données
        if "sqlalchemy" in error_msg.lower() or "database" in error_msg.lower():
            bugs.append({
                "type": "database_error",
                "error": error_msg
            })

        return bugs

    async def fix_bugs(self, code_files: Dict[str, str], bugs: List[Dict]) -> Dict[str, str]:
        """Corrige automatiquement les bugs identifiés"""

        fixed_code = code_files.copy()

        for bug in bugs:
            logger.info(f"🔧 Correction: {bug['type']}")

            if bug["type"] == "missing_dependency":
                # Ajouter le module manquant
                module = bug["module"]
                requirements = fixed_code.get("requirements.txt", "")

                # Mapper les noms de modules aux packages pip
                module_mapping = {
                    "jwt": "PyJWT",
                    "PIL": "Pillow",
                    "cv2": "opencv-python",
                    "yaml": "PyYAML",
                    "dotenv": "python-dotenv",
                    "email_validator": "email-validator",
                    "loguru": "loguru"
                }

                package = module_mapping.get(module, module)

                if package not in requirements:
                    fixed_code["requirements.txt"] = requirements + f"\n{package}"
                    logger.info(f"✅ Ajouté {package} à requirements.txt")

            elif bug["type"] == "syntax_error":
                # Utiliser le LLM pour corriger la syntaxe
                file_path = bug["file"]
                if file_path in fixed_code:
                    prompt = f"""Corrige cette erreur de syntaxe Python:

Fichier: {file_path}
Ligne: {bug['line']}
Erreur: {bug['error']}

Code actuel:
```python
{fixed_code[file_path]}
```

IMPORTANT: Réponds UNIQUEMENT avec le code Python corrigé complet, sans markdown ni explication.
"""

                    try:
                        corrected_code = await self.llm_client.generate_with_gemini_async(prompt)
                        # Nettoyer les balises markdown
                        corrected_code = self._clean_code(corrected_code)
                        fixed_code[file_path] = corrected_code
                        logger.info(f"✅ Corrigé {file_path}")
                    except Exception as e:
                        logger.error(f"Erreur correction syntaxe", error=str(e))

            elif bug["type"] == "import_error":
                # Corriger l'import erroné
                name = bug["name"]
                module = bug["module"]

                prompt = f"""Corrige cette erreur d'import:
ImportError: cannot import name '{name}' from '{module}'

Analyse tous les fichiers et corrige les imports incorrects.
Le nom '{name}' n'existe pas dans '{module}'.

RÈGLES:
- Vérifie que le nom importé existe réellement
- Utilise les bons noms (ex: UserBase au lieu de UserSchema)
- N'importe pas depuis des sous-modules inexistants (ex: models.user)

Identifie quel fichier a l'import incorrect et retourne le code corrigé.
"""

                # Pour l'instant, logger seulement (nécessite analyse multi-fichiers)
                logger.info(f"⚠️ Import error détecté: {name} depuis {module}")

        return fixed_code

    def _clean_code(self, code: str) -> str:
        """Nettoie le code des balises markdown"""
        if "```python" in code:
            start = code.find("```python") + 9
            end = code.find("```", start)
            if end != -1:
                code = code[start:end]
        elif code.startswith("```"):
            lines = code.split('\n')
            code = '\n'.join(lines[1:-1]) if len(lines) > 2 else code

        return code.strip()
