import pytest
from fastapi_ssii.webhook_sender import async_generation_task
from fastapi_ssii import project_store
import asyncio

pytestmark = pytest.mark.asyncio

async def test_auto_generate_repo_name_if_not_provided(mocker):
    """
    Vérifie que le nom du dépôt est généré s'il n'est pas fourni.
    """
    # Mocker toutes les dépendances externes
    mock_project_manager = mocker.patch('fastapi_ssii.agents.project_manager.generate_project', return_value={"code": {}})
    mock_devops_agent = mocker.patch('fastapi_ssii.agents.devops_agent.create_and_push_to_github')
    # Mocker la fonction qui génère le nom
    mock_generate_repo_name = mocker.patch('fastapi_ssii.webhook_sender.generate_repo_name', new_callable=mocker.AsyncMock, return_value="auto-name")

    project_id = project_store.create_new_project("Test")
    github_options = {"repo_name": "", "is_private": True}

    # Exécuter la tâche
    await async_generation_task(project_id, "Test", None, github_options)

    # Vérifier que la génération de nom a été appelée
    mock_generate_repo_name.assert_awaited_once()

    # Attendre que le thread DevOps ait une chance de s'exécuter
    await asyncio.sleep(0.1)

    # Vérifier que l'agent DevOps a été appelé avec le nom généré
    mock_devops_agent.assert_called_once()
    assert mock_devops_agent.call_args[1]['repo_name'] == "auto-name"

async def test_use_provided_repo_name_if_exists(mocker):
    """
    Vérifie que le nom du dépôt fourni est utilisé et que la génération automatique n'est pas appelée.
    """
    mock_project_manager = mocker.patch('fastapi_ssii.agents.project_manager.generate_project', return_value={"code": {}})
    mock_devops_agent = mocker.patch('fastapi_ssii.agents.devops_agent.create_and_push_to_github')
    mock_generate_repo_name = mocker.patch('fastapi_ssii.webhook_sender.generate_repo_name', new_callable=mocker.AsyncMock)

    project_id = project_store.create_new_project("Test")
    github_options = {"repo_name": "provided-name", "is_private": True}

    await async_generation_task(project_id, "Test", None, github_options)

    # Vérifier que la génération de nom N'A PAS été appelée
    mock_generate_repo_name.assert_not_awaited()

    await asyncio.sleep(0.1)

    # Vérifier que l'agent DevOps a été appelé avec le nom fourni
    mock_devops_agent.assert_called_once()
    assert mock_devops_agent.call_args[1]['repo_name'] == "provided-name"
