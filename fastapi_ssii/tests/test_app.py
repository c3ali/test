from fastapi.testclient import TestClient
from fastapi_ssii.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_project():
    response = client.post(
        "/generate_project",
        json={"description": "A simple blog API"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Project generation completed for: A simple blog API"
    assert "main.py" in data["code"]
    assert "tests/test_main.py" in data["code"]
    assert "index.html" in data["code"]
    assert "style.css" in data["code"]
    assert "script.js" in data["code"]
