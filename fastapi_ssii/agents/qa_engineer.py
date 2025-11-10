from fastapi_ssii import gemini_client

def generate_tests(plan: dict, backend_code: dict) -> dict:
    """
    Génère les tests pour le code du backend en utilisant l'API Gemini.

    Args:
        plan: Le plan du projet généré par l'architecte.
        backend_code: Le code du backend généré par le développeur.

    Returns:
        Un dictionnaire contenant le code des fichiers de test.
    """
    generated_tests = {}

    test_files = [f for f in plan.get("files", {}).keys() if f.startswith("tests/")]

    for test_filename in test_files:
        # Trouver le fichier source correspondant au test
        source_filename = test_filename.replace("tests/test_", "").replace(".py", ".py") # Simplistic mapping
        source_code = backend_code.get(source_filename, f"# Le code source pour {source_filename} n'a pas été trouvé.")

        prompt = f"""
        En tant qu'ingénieur QA expert en Python, écris les tests unitaires pour le fichier `{test_filename}`.

        **Objectif du test :**
        Tester le code contenu dans le fichier `{source_filename}`.

        **Code source à tester :**
        ```python
        {source_code}
        ```

        **Contexte global du projet :**
        Le projet est une application FastAPI. Le plan général est : {plan['files']}.
        Les dépendances, y compris les outils de test, sont : {plan['dependencies']}.

        **Instructions :**
        - Écris des tests en utilisant le framework `pytest`.
        - Si le code source est une application FastAPI, utilise `TestClient`.
        - Les tests doivent être pertinents, couvrir les cas nominaux et les cas limites.
        - Ne fournis que le code Python brut pour le fichier de test, sans aucun texte explicatif ou formatage Markdown.
        """

        print(f"Génération des tests pour : {test_filename}...")
        test_code = gemini_client.generate_with_gemini(prompt)

        # Nettoyer la réponse pour enlever les blocs de code Markdown
        if test_code.startswith("```python"):
            test_code = test_code[9:-4].strip()

        generated_tests[test_filename] = test_code

    return generated_tests
