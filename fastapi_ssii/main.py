from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional
from fastapi_ssii.webhook_sender import generation_task

# --- Modèles Pydantic ---

class ProjectRequest(BaseModel):
    description: str
    response_webhook_url: HttpUrl # Rendu obligatoire pour ce point de terminaison

class ImmediateResponse(BaseModel):
    status: str
    message: str

# --- Application FastAPI ---

app = FastAPI(
    title="SSII World Class Agency (Async with Webhooks)",
    description="Une API pour générer du code de manière asynchrone et notifier via webhook.",
    version="0.3.0",
)

# --- Points de terminaison de l'API ---

@app.get("/", tags=["Health Check"])
def read_root():
    """Point de terminaison simple pour vérifier si le service est en ligne."""
    return {"status": "ok"}

@app.post("/generate_project_async", response_model=ImmediateResponse, tags=["Code Generation"])
async def generate_project_async(
    request: ProjectRequest,
    background_tasks: BackgroundTasks
):
    """
    Accepte une demande de génération, démarre le processus en arrière-plan
    et renvoie une confirmation immédiate.
    """
    # Ajoute la tâche de longue durée à exécuter en arrière-plan
    background_tasks.add_task(
        generation_task,
        request.description,
        request.response_webhook_url
    )

    return {
        "status": "accepted",
        "message": "La demande de génération a été acceptée et est en cours de traitement."
    }
