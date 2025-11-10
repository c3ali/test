import json
from fastapi.testclient import TestClient
from fastapi_ssii.main import app

client = TestClient(app)

def test_health_check():
    """Teste si le point de terminaison de santé fonctionne."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_project_with_mocked_gemini(mocker):
    """
    Teste le workflow de génération de projet en simulant les réponses de Gemini.
    """
    # 1. Préparer les fausses réponses de Gemini pour chaque agent

    # Réponse simulée pour l'architecte
    mock_plan = {
      "files": {
        "main.py": "Point d'entrée FastAPI.",
        "tests/test_main.py": "Tests pour main.py."
      },
      "dependencies": ["fastapi", "pytest"]
    }

    # Réponses simulées pour le développeur backend
    mock_backend_code = "from fastapi import FastAPI\napp = FastAPI()"

    # Réponses simulées pour le développeur frontend
    mock_frontend_code_html = "<h1>Mock Frontend</h1>"

    # Réponses simulées pour l'ingénieur QA
    mock_qa_code = "from main import app\ndef test_read_main(): pass"

    # Configurer le mock pour retourner les réponses dans le bon ordre
    mocker.patch(
        'fastapi_ssii.gemini_client.generate_with_gemini',
        side_effect=[
            # 1. Appel de l'architecte
            json.dumps(mock_plan),
            # 2. Appel du dev backend pour main.py
            mock_backend_code,
            # 3. Appels du dev frontend
            mock_frontend_code_html, # index.html
            "/* mock css */",      # style.css
            "// mock js",           # script.js
            # 4. Appel de l'ingénieur QA pour tests/test_main.py
            mock_qa_code
        ]
    )

    # 2. Exécuter la requête API
    response = client.post(
        "/generate_project",
        json={"description": "Une API simple"}
    )

    # 3. Valider la réponse
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Projet généré avec succès !"
    assert data["plan"] == mock_plan

    # Vérifier que le code généré correspond aux mocks
    assert "main.py" in data["code"]
    assert data["code"]["main.py"] == mock_backend_code

    assert "index.html" in data["code"]
    assert data["code"]["index.html"] == mock_frontend_code_html

    assert "tests/test_main.py" in data["code"]
    assert data["code"]["tests/test_main.py"] == mock_qa_code
