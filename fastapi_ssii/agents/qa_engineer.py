def generate_tests(code: dict) -> dict:
    """
    Generates tests for the provided code.
    For now, returns a simple test for the main endpoint.
    """
    tests = {}
    for filename, file_code in code.items():
        if "main.py" in filename:
            tests["tests/test_main.py"] = """from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from your generated FastAPI app!"}
"""
    return tests
