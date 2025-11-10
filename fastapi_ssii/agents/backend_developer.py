from fastapi_ssii import gemini_client
import json
import asyncio

async def generate_code(plan: dict) -> dict:
    """
    Génère le code initial du backend pour chaque fichier du plan de manière asynchrone.
    """
    tasks = []
    backend_files = {f: d for f, d in plan.get("files", {}).items() if not f.startswith("tests/") and f.endswith(".py")}

    for filename, description in backend_files.items():
        prompt = f"""
        En tant que développeur Python expert, écris le code pour le fichier `{filename}`.
        (Le reste du prompt reste le même...)
        """
        # Crée une coroutine pour chaque génération de fichier
        tasks.append(generate_file(filename, prompt))

    # Exécute toutes les générations de fichiers en parallèle
    generated_files = await asyncio.gather(*tasks)

    # Convertit la liste de tuples (nom, code) en dictionnaire
    return {filename: code for filename, code in generated_files}


async def refine_code(plan: dict, existing_code: dict, feedback: str) -> dict:
    """
    Raffine le code existant de manière asynchrone.
    """
    # (La logique de raffinement peut aussi être rendue asynchrone)
    # Pour l'instant, nous nous concentrons sur la génération initiale.
    return {}

async def generate_file(filename: str, prompt: str) -> (str, str):
    """
    Fonction utilitaire asynchrone pour générer un seul fichier.
    """
    print(f"Démarrage de la génération asynchrone pour : {filename}...")
    code = await gemini_client.generate_with_gemini_async(prompt)

    if code.startswith("```python"):
        code = code[9:-4].strip()

    print(f"Terminé : {filename}")
    return filename, code
