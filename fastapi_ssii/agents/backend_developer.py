def generate_backend_code(plan: dict) -> dict:
    """
    Generates the backend code based on the project plan.
    For now, returns hardcoded code for the files specified in the plan.
    """
    code = {}
    for filename, description in plan.get("files", {}).items():
        if "main.py" in filename:
            code[filename] = """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from your generated FastAPI app!"}
"""
        elif "models.py" in filename:
            code[filename] = "# Pydantic models will be defined here."
        elif "database.py" in filename:
            code[filename] = "# Database connection logic will be here."
        elif "crud.py" in filename:
            code[filename] = "# CRUD operations will be defined here."
        elif "schemas.py" in filename:
            code[filename] = "# Pydantic schemas will be defined here."
        else:
            code[filename] = f"# {description}"

    return code
