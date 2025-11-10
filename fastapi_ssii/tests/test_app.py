from fastapi.testclient import TestClient
from fastapi_ssii.main import app
from fastapi_ssii import project_store
import uuid

client = TestClient(app)

def test_read_frontend_index():
    """Vérifie que la page d'accueil est bien servie."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

def test_read_frontend_static_files():
    """Vérifie que les fichiers statiques (CSS, JS) sont accessibles."""
    response_css = client.get("/static/style.css")
    assert response_css.status_code == 200
    assert "text/css" in response_css.headers['content-type']

    response_js = client.get("/static/script.js")
    assert response_js.status_code == 200
    # Correction : Le content-type peut être 'text/javascript'
    assert "javascript" in response_js.headers['content-type']

def test_get_project_status_success():
    """Vérifie qu'on peut récupérer le statut d'un projet existant."""
    desc = "Projet de test de statut"
    project_id = project_store.create_new_project(desc)
    project_store.update_project(project_id, {"status": "completed", "code": {"main.py": "print('ok')"}})

    response = client.get(f"/project_status/{project_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["description"] == desc
    assert data["status"] == "completed"
    assert data["code"]["main.py"] == "print('ok')"

def test_get_project_status_not_found():
    """Vérifie qu'une erreur 404 est retournée pour un projet inconnu."""
    unknown_id = str(uuid.uuid4())
    response = client.get(f"/project_status/{unknown_id}")
    assert response.status_code == 404

def test_generate_project_creates_project_and_starts_task(mocker):
    """Vérifie que l'endpoint de génération fonctionne."""
    mock_add_task = mocker.patch('fastapi.BackgroundTasks.add_task')
    request_data = {"description": "Test de génération"}

    response = client.post("/generate_project_async", json=request_data)

    assert response.status_code == 200
    project_id = response.json().get("project_id")
    assert project_id is not None
    mock_add_task.assert_called_once()

def test_refine_project_starts_refinement_task(mocker):
    """Vérifie que l'endpoint de raffinement fonctionne."""
    mock_add_task = mocker.patch('fastapi.BackgroundTasks.add_task')
    project_id = project_store.create_new_project("Projet à raffiner")
    request_data = {"feedback": "Feedback de test"}

    response = client.post(f"/refine_project/{project_id}", json=request_data)

    assert response.status_code == 200
    assert response.json()["project_id"] == project_id
    mock_add_task.assert_called_once()
