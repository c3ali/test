from fastapi_ssii import gemini_client

def generate_backend_code(plan: dict) -> dict:
    """
    Génère le code du backend pour chaque fichier du plan en utilisant l'API Gemini.

    Args:
        plan: Le plan du projet généré par l'architecte.

    Returns:
        Un dictionnaire où les clés sont les noms de fichiers et les valeurs sont le code généré.
    """
    generated_code = {}

    # Exclure les fichiers de test, qui seront gérés par l'ingénieur QA
    backend_files = {f: d for f, d in plan.get("files", {}).items() if not f.startswith("tests/")}

    for filename, description in backend_files.items():
        prompt = f"""
        En tant que développeur Python expert, écris le code pour le fichier `{filename}`.

        **Description du rôle du fichier :**
        {description}

        **Contexte global du projet :**
        Le projet est une application web dont le plan général est le suivant : {plan['files']}.
        Les dépendances prévues sont : {plan['dependencies']}.

        **Instructions :**
        - Écris du code Python propre, fonctionnel et bien documenté.
        - Ne fournis que le code brut, sans aucun texte explicatif, commentaire d'introduction ou formatage Markdown.
        - Assure-toi que le code est cohérent avec le rôle des autres fichiers prévus.
        """

        print(f"Génération du code pour : {filename}...")
        code = gemini_client.generate_with_gemini(prompt)

        # Nettoyer la réponse pour enlever les blocs de code Markdown
        if code.startswith("```python"):
            code = code[9:-4].strip()

        generated_code[filename] = code

    return generated_code
