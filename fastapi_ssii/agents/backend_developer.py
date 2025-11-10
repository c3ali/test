from fastapi_ssii import gemini_client
import json

def generate_code(plan: dict) -> dict:
    """
    Génère le code initial du backend pour chaque fichier du plan en utilisant l'API Gemini.
    """
    generated_code = {}

    backend_files = {f: d for f, d in plan.get("files", {}).items() if not f.startswith("tests/") and f.endswith(".py")}

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

        if code.startswith("```python"):
            code = code[9:-4].strip()

        generated_code[filename] = code

    return generated_code


def refine_code(plan: dict, existing_code: dict, feedback: str) -> dict:
    """
    Raffine le code existant en se basant sur le feedback.
    """
    analysis_prompt = f"""
    En tant qu'analyste de code, lis le feedback suivant et détermine quel fichier du projet doit être modifié.

    **Plan du projet (fichiers et leurs rôles) :**
    {json.dumps(plan['files'], indent=2)}

    **Feedback de l'utilisateur :**
    "{feedback}"

    **Ta réponse doit être UNIQUEMENT le nom du fichier à modifier (par exemple, "main.py").**
    """

    file_to_modify = gemini_client.generate_with_gemini(analysis_prompt).strip()

    if file_to_modify not in existing_code:
        print(f"L'analyse a déterminé un fichier invalide à modifier : {file_to_modify}")
        return {}

    print(f"L'analyse a déterminé que le fichier à modifier est : {file_to_modify}")

    code_to_modify = existing_code.get(file_to_modify, "")

    refinement_prompt = f"""
    En tant que développeur Python expert, modifie le code existant suivant en te basant sur le feedback fourni.

    **Fichier à modifier :** `{file_to_modify}`
    **Rôle de ce fichier :** {plan['files'].get(file_to_modify, "Non défini")}

    **Code existant :**
    ```python
    {code_to_modify}
    ```

    **Feedback de l'utilisateur / Instructions de modification :**
    "{feedback}"

    **Instructions :**
    - Réécris le fichier complet avec les modifications demandées.
    - Assure-toi que le nouveau code est propre, correct et répond au feedback.
    - Ne fournis que le code Python brut, sans aucun texte explicatif ou formatage Markdown.
    """

    refined_code_str = gemini_client.generate_with_gemini(refinement_prompt)

    if refined_code_str.startswith("```python"):
        refined_code_str = refined_code_str[9:-4].strip()

    return {file_to_modify: refined_code_str}
