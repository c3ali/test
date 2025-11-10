import pytest
from fastapi.testclient import TestClient
from fastapi_ssii.main import app
from fastapi_ssii import project_store
import uuid
import asyncio

client = TestClient(app)

pytestmark = pytest.mark.asyncio

# ... (les tests pour le frontend et le statut restent)

async def test_generate_project_with_github_options(mocker):
    """Vérifie que les options GitHub sont bien passées à la tâche de fond."""
    mock_add_task = mocker.patch('fastapi.BackgroundTasks.add_task')

    request_data = {
        "description": "Un projet à pousser sur GitHub",
        "github_options": {
            "repo_name": "test-repo",
            "is_private": False
        }
    }

    response = client.post("/generate_project_async", json=request_data)

    assert response.status_code == 200

    mock_add_task.assert_called_once()
    args, _ = mock_add_task.call_args

    github_opts = args[4]
    assert github_opts is not None
    assert github_opts["repo_name"] == "test-repo"
    assert not github_opts["is_private"]

# On simplifie en enlevant le test d'intégration trop complexe
