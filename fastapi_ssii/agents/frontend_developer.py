from fastapi_ssii import gemini_client

def generate_frontend_code(plan: dict) -> dict:
    """
    Génère le code du frontend (HTML, CSS, JS) en utilisant l'API Gemini.

    Args:
        plan: Le plan du projet généré par l'architecte.

    Returns:
        Un dictionnaire contenant le code des fichiers frontend.
    """
    generated_code = {}

    # Définir les fichiers frontend à générer. On peut aussi les extraire du plan si l'architecte les a inclus.
    frontend_files = {
        "index.html": "Une page HTML de base pour l'application.",
        "style.css": "Une feuille de style CSS pour un design simple et propre.",
        "script.js": "Un fichier JavaScript pour l'interactivité de base."
    }

    for filename, description in frontend_files.items():
        # Déterminer le langage pour le prompt
        lang = "HTML" if filename.endswith(".html") else "CSS" if filename.endswith(".css") else "JavaScript"

        prompt = f"""
        En tant que développeur web full-stack, écris le code pour le fichier `{filename}`.

        **Description du rôle du fichier :**
        {description}

        **Contexte global du projet :**
        Le projet est une application web dont le backend est décrit par le plan suivant : {plan['files']}.
        Le but est de créer une interface simple pour interagir avec ce backend.

        **Instructions :**
        - Écris du code {lang} standard, moderne et bien structuré.
        - Pour le HTML, inclus une structure de base (doctype, head, body).
        - Pour le JavaScript, assure-toi que le code est simple et commente son objectif.
        - Ne fournis que le code brut, sans aucun texte explicatif ou formatage Markdown.
        """

        print(f"Génération du code pour : {filename}...")
        code = gemini_client.generate_with_gemini(prompt)

        # Nettoyer la réponse pour enlever les blocs de code Markdown
        if code.startswith(f"```{lang.lower()}"):
            code = code[len(lang)+4:-4].strip()

        generated_code[filename] = code

    return generated_code
