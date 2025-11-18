from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from fastapi_ssii.webhook_sender import generation_task, refinement_task
from fastapi_ssii import project_store

# --- Modèles Pydantic ---

class GitHubOptions(BaseModel):
    repo_name: str
    is_private: bool = True

class ProjectRequest(BaseModel):
    description: str
    response_webhook_url: Optional[HttpUrl] = None
    github_options: Optional[GitHubOptions] = None
    auto_deploy: bool = False  # Nouveau: déploiement automatique

class ImmediateResponse(BaseModel):
    status: str
    message: str
    project_id: str

# (Le reste des modèles Pydantic reste le même)
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
    title="Autonomous Code Generation Platform",
    description="Génère, déploie et corrige automatiquement des applications complètes avec Railway et Supabase.",
    version="1.0.0",
)

# (Le reste de l'application reste le même)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def read_index():
    return "frontend/index.html"

@app.get("/project_status/{project_id}", response_model=ProjectStatusResponse, tags=["Project Status"])
async def get_project_status(project_id: str):
    project = project_store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return project

@app.post("/generate_project_async", response_model=ImmediateResponse, tags=["Code Generation"])
async def generate_project_async(
    request: ProjectRequest,
    background_tasks: BackgroundTasks
):
    """
    Génère un projet complet.

    Si auto_deploy=True, déploie automatiquement sur Railway + Supabase.
    Nécessite les tokens RAILWAY_TOKEN et/ou SUPABASE_ACCESS_TOKEN dans .env
    """
    project_id = project_store.create_new_project(request.description)

    background_tasks.add_task(
        generation_task,
        project_id,
        request.description,
        request.response_webhook_url,
        request.github_options.model_dump() if request.github_options else None,
        request.auto_deploy  # Nouveau paramètre
    )

    deploy_msg = " + déploiement automatique" if request.auto_deploy else ""

    return {
        "status": "accepted",
        "message": f"La demande de génération{deploy_msg} a été acceptée.",
        "project_id": project_id,
    }

# (Le point de terminaison de raffinement reste le même pour l'instant)
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
