import pytest
from fastapi.testclient import TestClient
from fastapi_ssii.main import app
from fastapi_ssii import project_store
import uuid
import asyncio

client = TestClient(app)

# Marquer tous les tests de ce module pour qu'ils s'exécutent avec asyncio
pytestmark = pytest.mark.asyncio


async def test_read_frontend_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

async def test_get_project_status_success():
    desc = "Projet de test de statut"
    project_id = project_store.create_new_project(desc)

    response = client.get(f"/project_status/{project_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id

async def test_generate_project_async_starts_task(mocker):
    """Vérifie que la coroutine de génération est bien appelée."""
    # Créer un mock pour la coroutine elle-même
    # mocker.AsyncMock() est la bonne façon de mocker une coroutine
    mock_async_generation_task = mocker.patch('fastapi_ssii.webhook_sender.async_generation_task', new_callable=mocker.AsyncMock)

    request_data = {"description": "Test de génération"}
    response = client.post("/generate_project_async", json=request_data)

    assert response.status_code == 200

    # Attendre un court instant pour que la tâche de fond ait une chance de démarrer
    await asyncio.sleep(0.1)

    # Vérifier que la coroutine a été appelée
    mock_async_generation_task.assert_awaited_once()

async def test_refine_project_async_starts_task(mocker):
    """Vérifie que la coroutine de raffinement est bien appelée."""
    mock_async_refinement_task = mocker.patch('fastapi_ssii.webhook_sender.async_refinement_task', new_callable=mocker.AsyncMock)

    project_id = project_store.create_new_project("Projet à raffiner")
    request_data = {"feedback": "Feedback de test"}

    response = client.post(f"/refine_project/{project_id}", json=request_data)

    assert response.status_code == 200

    await asyncio.sleep(0.1)

    mock_async_refinement_task.assert_awaited_once()
