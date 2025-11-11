from fastapi_ssii.agents.architect_agent import ArchitectAgent
from fastapi_ssii.agents.backend_agent import BackendAgent
from fastapi_ssii.agents.frontend_agent import FrontendAgent
from fastapi_ssii.agents.qa_agent import QAAgent
from fastapi_ssii.agents.business_analyst_agent import BusinessAnalystAgent
from fastapi_ssii import gemini_client
from fastapi_ssii.core.logger import get_logger
from fastapi_ssii.core.context_manager import ContextManager
import asyncio

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.agents = {
            "business_analyst": BusinessAnalystAgent(llm_client),
            "architect": ArchitectAgent(llm_client),
            "backend": BackendAgent(llm_client),
            "frontend": FrontendAgent(llm_client),
            "qa": QAAgent(llm_client),
        }

    async def generate_project(self, description: str) -> dict:
        context = ContextManager()

        logger.info("Phase 1: Business Analysis")
        try:
            tech_spec = await self.agents["business_analyst"].generate({"description": description})
            # On enrichit la spécification pour les agents suivants
            specification = {"description": description, "tech_spec": tech_spec, "context": context}
        except Exception as e:
            return {"error": f"Business Analysis failed: {e}"}

        logger.info("Phase 2: Architecture")
        try:
            plan = await self.agents["architect"].generate(specification)
            specification["plan"] = plan
        except Exception as e:
            return {"error": f"Architecture failed: {e}"}

        logger.info("Phase 3: Code Generation (Parallel)")
        backend_task = self.agents["backend"].generate(specification)
        frontend_task = self.agents["frontend"].generate(specification)

        results = await asyncio.gather(backend_task, frontend_task, return_exceptions=True)
        backend_code = results[0] if not isinstance(results[0], Exception) else {}
        frontend_code = results[1] if not isinstance(results[1], Exception) else {}

        specification["backend_code"] = backend_code

        logger.info("Phase 4: QA & Testing")
        tests = await self.agents["qa"].generate(specification)

        logger.info("Phase 5: Assembly")
        full_code = {**backend_code, **frontend_code, **tests}

        return {
            "message": "Project generated successfully!",
            "code": full_code,
            "plan": plan,
            "tech_spec": tech_spec
        }

orchestrator = Orchestrator(gemini_client)
