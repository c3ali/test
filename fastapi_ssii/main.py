from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from fastapi_ssii.webhook_sender import generation_task, refinement_task
from fastapi_ssii import project_store

# --- Modèles Pydantic ---

class ProjectRequest(BaseModel):
    description: str
    response_webhook_url: Optional[HttpUrl] = None

class ImmediateResponse(BaseModel):
    status: str
    message: str
    project_id: str

class RefineRequest(BaseModel):
    feedback: str
    response_webhook_url: Optional[HttpUrl] = None

class ProjectStatusResponse(BaseModel):
    id: str
    status: str
    description: str
    code: Dict[str, str]
    plan: Dict[str, Any]

# --- Application FastAPI ---

app = FastAPI(
    title="Interactive SSII Agency (Stateful)",
    description="Une API pour générer et raffiner du code de manière itérative, avec une interface web.",
    version="0.5.0",
)

# --- Service des fichiers statiques pour le Frontend ---
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def read_index():
    """Sert la page d'accueil de l'interface frontend."""
    return "frontend/index.html"

# --- Points de terminaison de l'API ---

@app.get("/project_status/{project_id}", response_model=ProjectStatusResponse, tags=["Project Status"])
async def get_project_status(project_id: str):
    """
    Récupère l'état complet d'un projet, y compris le code généré.
    """
    project = project_store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return project

@app.post("/generate_project_async", response_model=ImmediateResponse, tags=["Code Generation"])
async def generate_project_async(
    request: ProjectRequest,
    background_tasks: BackgroundTasks
):
    project_id = project_store.create_new_project(request.description)
    background_tasks.add_task(
        generation_task,
        project_id,
        request.description,
        request.response_webhook_url
    )
    return {
        "status": "accepted",
        "message": "La demande de génération a été acceptée.",
        "project_id": project_id,
    }

@app.post("/refine_project/{project_id}", response_model=ImmediateResponse, tags=["Code Refinement"])
async def refine_project_endpoint(
    project_id: str,
    request: RefineRequest,
    background_tasks: BackgroundTasks
):
    project = project_store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    background_tasks.add_task(
        refinement_task,
        project_id,
        request.feedback,
        request.response_webhook_url
    )
    return {
        "status": "accepted",
        "message": "La demande de raffinement a été acceptée.",
        "project_id": project_id,
    }
