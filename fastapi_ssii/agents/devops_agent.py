# fastapi_ssii/agents/devops_agent.py
import os
from github import Github, GithubException

def create_and_push_to_github(repo_name: str, code_files: dict, is_private: bool) -> str:
    """
    Crée un dépôt sur GitHub et y pousse les fichiers de code générés.

    Args:
        repo_name: Le nom du dépôt à créer.
        code_files: Un dictionnaire {nom_fichier: contenu}.
        is_private: True si le dépôt doit être privé.

    Returns:
        L'URL du nouveau dépôt, ou un message d'erreur.
    """
    github_token = os.getenv("GITHUB_ACCESS_TOKEN")

    if not github_token or github_token == "YOUR_GITHUB_ACCESS_TOKEN":
        error_msg = "Erreur : Le token d'accès GitHub n'est pas configuré."
        print(error_msg)
        return error_msg

    try:
        g = Github(github_token)
        user = g.get_user()

        print(f"Création du dépôt '{repo_name}' sur le compte de {user.login}...")

        # Créer le dépôt
        repo = user.create_repo(
            name=repo_name,
            private=is_private,
            auto_init=True  # Crée un README.md initial, essentiel pour pousser des fichiers ensuite
        )

        print(f"Dépôt créé avec succès : {repo.html_url}")

        # Pousser chaque fichier dans le dépôt
        for file_path, file_content in code_files.items():
            try:
                # Vérifier si le fichier existe déjà (pour les mises à jour futures)
                repo.get_contents(file_path)
                # Si oui, on le met à jour
                repo.update_file(
                    path=file_path,
                    message=f"Update {file_path}",
                    content=file_content,
                    sha=repo.get_contents(file_path).sha
                )
                print(f"Fichier mis à jour : {file_path}")
            except GithubException as e:
                if e.status == 404:
                    # Le fichier n'existe pas, on le crée
                    repo.create_file(
                        path=file_path,
                        message=f"Add {file_path}",
                        content=file_content
                    )
                    print(f"Fichier créé : {file_path}")
                else:
                    raise e

        return repo.html_url

    except GithubException as e:
        error_msg = f"Erreur lors de l'interaction avec GitHub : {e.data['message']}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Une erreur inattendue est survenue : {e}"
        print(error_msg)
        return error_msg
