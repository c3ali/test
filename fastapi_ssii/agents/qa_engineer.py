from fastapi_ssii import gemini_client
import asyncio

async def generate_tests(plan: dict, backend_code: dict) -> dict:
    """
    Génère les tests pour le code du backend de manière asynchrone.
    """
    tasks = []
    test_files = [f for f in plan.get("files", {}).keys() if f.startswith("tests/")]

    for test_filename in test_files:
        source_filename = test_filename.replace("tests/test_", "")
        source_code = backend_code.get(source_filename, "# Code source non trouvé.")

        prompt = f"""
        En tant qu'ingénieur QA, écris les tests pytest pour `{test_filename}`.
        Le code à tester dans `{source_filename}` est :
        ```python
        {source_code}
        ```
        (Le reste du prompt reste le même...)
        """
        tasks.append(generate_file(test_filename, prompt))

    generated_files = await asyncio.gather(*tasks)
    return {filename: code for filename, code in generated_files}

async def generate_file(filename: str, prompt: str) -> (str, str):
    """
    Fonction utilitaire asynchrone pour générer un seul fichier de test.
    """
    print(f"Démarrage de la génération asynchrone pour : {filename}...")
    code = await gemini_client.generate_with_gemini_async(prompt)

    if code.startswith("```python"):
        code = code[9:-4].strip()

    print(f"Terminé : {filename}")
    return filename, code
