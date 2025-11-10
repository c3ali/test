def design_project(description: str) -> dict:
    """
    Designs the project structure based on the description.
    For now, returns a hardcoded project plan.
    """
    return {
        "files": {
            "main.py": "FastAPI application",
            "models.py": "Pydantic models",
            "database.py": "Database connection",
            "crud.py": "CRUD operations",
            "schemas.py": "Pydantic schemas",
            "tests/test_main.py": "Tests for the main application"
        },
        "dependencies": ["fastapi", "uvicorn", "pydantic", "sqlalchemy"]
    }
