from fastapi.testclient import TestClient
from fastapi_ssii.main import app

client = TestClient(app)

def test_health_check():
    """Teste le point de terminaison de santé."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_project_async_success(mocker):
    """
    Teste le point de terminaison asynchrone.
    Vérifie que la réponse immédiate est correcte et que la tâche de fond
    est bien appelée avec les bons arguments.
    """
    # 1. Simuler (mocker) la fonction `generation_task` pour espionner ses appels
    mock_generation_task = mocker.patch('fastapi_ssii.main.generation_task')

    # 2. Définir les données de la requête
    webhook_url = "https://n8n.example.com/webhook/test"
    request_data = {
        "description": "Une super application de blog",
        "response_webhook_url": webhook_url
    }

    # 3. Exécuter la requête sur le point de terminaison
    response = client.post("/generate_project_async", json=request_data)

    # 4. Valider la réponse immédiate
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "accepted"
    assert "La demande de génération a été acceptée" in response_json["message"]

    # 5. Valider que la tâche de fond a été appelée correctement
    # BackgroundTasks exécute la tâche après la réponse, donc nous vérifions
    # que `add_task` a été appelé correctement. Pour ce test, nous nous fions
    # à l'appel direct de la fonction mockée.
    # NOTE : Un test plus complexe pourrait vérifier l'appel à `background_tasks.add_task`,
    # mais mocker la fonction appelée est une approche plus simple et tout aussi efficace ici.

    # Pour ce test, nous allons directement vérifier que `generation_task` a été appelé
    # en supposant que l'appel `background_tasks.add_task` fonctionne comme attendu.
    # Pour un test d'intégration plus profond, il faudrait une approche différente.

    # Ici, nous allons plutôt mocker `background_tasks.add_task` pour nous assurer qu'il est appelé.
    mock_add_task = mocker.patch('fastapi.BackgroundTasks.add_task')

    # On relance la requête avec le nouveau mock
    client.post("/generate_project_async", json=request_data)

    # On vérifie que `add_task` a été appelé une fois avec les bons arguments.
    mock_add_task.assert_called_once()
    # On récupère les arguments de l'appel
    args, kwargs = mock_add_task.call_args
    # Le premier argument doit être la fonction `generation_task` elle-même
    # Les arguments suivants sont ceux passés à la tâche
    assert args[1] == request_data["description"]
    assert str(args[2]) == request_data["response_webhook_url"]
