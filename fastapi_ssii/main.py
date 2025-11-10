from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_ssii.agents import project_manager

class ProjectRequest(BaseModel):
    description: str

class ProjectResponse(BaseModel):
    message: str
    code: dict

app = FastAPI(
    title="SSII World Class Agency",
    description="An API to generate code based on a project description, simulating a world-class SSII.",
    version="0.1.0",
)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple endpoint to check if the service is running."""
    return {"status": "ok"}

@app.post("/generate_project", response_model=ProjectResponse, tags=["Code Generation"])
def generate_project(request: ProjectRequest):
    """
    Receives a project description and returns the generated code.
    """
    # The orchestration logic is now handled by the project manager.
    generated_code = project_manager.generate_project(request.description)

    return {
        "message": f"Project generation completed for: {request.description}",
        "code": generated_code
    }
