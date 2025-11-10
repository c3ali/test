from fastapi_ssii import gemini_client
import asyncio

async def generate_code(plan: dict) -> dict:
    """
    Génère le code du frontend de manière asynchrone.
    """
    tasks = []
    frontend_files = {
        "index.html": "Une page HTML de base...",
        "style.css": "Une feuille de style CSS...",
        "script.js": "Un fichier JavaScript..."
    }

    for filename, description in frontend_files.items():
        lang = "HTML" if filename.endswith(".html") else "CSS" if filename.endswith(".css") else "JavaScript"
        prompt = f"""
        En tant que développeur web, écris le code pour `{filename}`.
        (Le reste du prompt reste le même...)
        """
        tasks.append(generate_file(filename, prompt, lang))

    generated_files = await asyncio.gather(*tasks)
    return {filename: code for filename, code in generated_files}

async def generate_file(filename: str, prompt: str, lang: str) -> (str, str):
    """
    Fonction utilitaire asynchrone pour générer un seul fichier frontend.
    """
    print(f"Démarrage de la génération asynchrone pour : {filename}...")
    code = await gemini_client.generate_with_gemini_async(prompt)

    if code.startswith(f"```{lang.lower()}"):
        code = code[len(lang)+4:-4].strip()

    print(f"Terminé : {filename}")
    return filename, code
