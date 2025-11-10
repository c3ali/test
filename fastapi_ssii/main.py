from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_ssii.agents import project_manager
from typing import Dict, List, Any

class ProjectRequest(BaseModel):
    description: str

class ProjectResponse(BaseModel):
    message: str
    code: Dict[str, str]
    plan: Dict[str, Any]

app = FastAPI(
    title="SSII World Class Agency (powered by Gemini)",
    description="An API to generate code based on a project description, using a multi-agent system powered by Gemini.",
    version="0.2.0",
)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple endpoint to check if the service is running."""
    return {"status": "ok"}

@app.post("/generate_project", response_model=ProjectResponse, tags=["Code Generation"])
def generate_project(request: ProjectRequest):
    """
    Receives a project description and returns the generated code, plan, and dependencies.
    """
    # L'orchestration est entièrement gérée par le project_manager
    generation_result = project_manager.generate_project(request.description)

    # Si la génération a échoué, on retourne une réponse d'erreur
    if "error" in generation_result:
        return {
            "message": "Project generation failed.",
            "code": {"error.log": generation_result["error"]},
            "plan": generation_result.get("plan", {})
        }

    return generation_result
