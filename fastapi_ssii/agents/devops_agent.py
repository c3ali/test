from fastapi_ssii.agents.base_agent import BaseAgent
from fastapi_ssii.core.logger import get_logger
import os
from github import Github, GithubException
from typing import Dict, Any, List

logger = get_logger(__name__)

class DevOpsAgent(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__("DevOpsAgent", llm_client)

    async def generate(self, specification: Dict[str, Any]) -> Dict[str, str]:
        # ... (La logique de generate reste la même)
        pass

    def create_and_push_to_github(self, repo_name: str, code_files: dict, is_private: bool) -> str:
        github_token = os.getenv("GITHUB_ACCESS_TOKEN")
        if not github_token or github_token == "YOUR_GITHUB_ACCESS_TOKEN":
            logger.error("Token GitHub non configuré.")
            return "Erreur: Token GitHub non configuré."

        try:
            g = Github(github_token)
            user = g.get_user()
            logger.info(f"Création du dépôt '{repo_name}' pour l'utilisateur {user.login}.")

            repo = user.create_repo(name=repo_name, private=is_private, auto_init=True)
            logger.info(f"Dépôt créé : {repo.html_url}")

            for file_path, file_content in code_files.items():
                try:
                    repo.create_file(path=file_path, message=f"Add {file_path}", content=file_content)
                    logger.info(f"Fichier poussé : {file_path}")
                except GithubException as e:
                    if e.status == 422: # Le fichier existe déjà
                        # Logique de mise à jour si nécessaire
                        logger.warn(f"Le fichier {file_path} existe déjà. Ignoré.")
                    else:
                        raise e
            return repo.html_url

        except GithubException as e:
            msg = e.data.get("message", "Erreur inconnue")
            logger.error(f"Erreur GitHub : {msg}", error_details=e.data)
            return f"Erreur GitHub : {msg}"
        except Exception as e:
            logger.error(f"Erreur inattendue de l'agent DevOps.", error=str(e))
            return f"Erreur inattendue : {e}"

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        # ... (La logique de validation reste la même)
        pass
