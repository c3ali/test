from fastapi_ssii.agents.base_agent import BaseAgent
from fastapi_ssii.core.logger import get_logger
import httpx
import asyncio
import os
import secrets
import string
from typing import Dict, Any, List, Optional

logger = get_logger(__name__)

class DeploymentAgent(BaseAgent):
    """Agent autonome pour déployer sur Railway et configurer Supabase"""

    def __init__(self, llm_client=None):
        super().__init__("DeploymentAgent", llm_client)
        self.railway_token = os.getenv("RAILWAY_TOKEN")
        self.supabase_token = os.getenv("SUPABASE_ACCESS_TOKEN")

    async def generate(self, specification: Dict[str, Any]) -> Dict[str, str]:
        """
        Déploie l'application complète avec base de données.
        Retourne les URLs et credentials.
        """
        result = {}

        try:
            # 1. Créer la base de données Supabase
            if self.supabase_token:
                logger.info("Création du projet Supabase...")
                db_config = await self.create_supabase_project(specification)
                result["database"] = db_config
            else:
                logger.info("Token Supabase manquant, skip création DB")
                result["database"] = {"status": "skipped"}

            # 2. Déployer sur Railway
            if self.railway_token:
                logger.info("Déploiement sur Railway...")
                deployment = await self.deploy_to_railway(
                    specification,
                    result.get("database", {})
                )
                result["deployment"] = deployment
            else:
                logger.info("Token Railway manquant, skip déploiement")
                result["deployment"] = {"status": "skipped"}

        except Exception as e:
            logger.error(f"Erreur lors du déploiement", error=str(e))
            result["error"] = str(e)

        return result

    async def create_supabase_project(self, spec: Dict) -> Dict:
        """Crée un projet Supabase avec base de données"""

        project_name = spec.get("tech_spec", {}).get("project_summary", "project")[:32]
        db_password = self._generate_secure_password()

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Récupérer l'organisation
            org_response = await client.get(
                "https://api.supabase.com/v1/organizations",
                headers={"Authorization": f"Bearer {self.supabase_token}"}
            )

            if org_response.status_code != 200:
                raise Exception(f"Cannot fetch organizations: {org_response.text}")

            orgs = org_response.json()
            if not orgs:
                raise Exception("No Supabase organization found")

            org_id = orgs[0]["id"]

            # Créer le projet
            logger.info(f"Création du projet Supabase: {project_name}")
            project_response = await client.post(
                "https://api.supabase.com/v1/projects",
                headers={
                    "Authorization": f"Bearer {self.supabase_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": project_name,
                    "organization_id": org_id,
                    "plan": "free",
                    "region": "us-east-1",
                    "db_pass": db_password
                }
            )

            if project_response.status_code not in [200, 201]:
                raise Exception(f"Cannot create project: {project_response.text}")

            project = project_response.json()
            project_id = project["id"]

            # Attendre que le projet soit prêt (max 5 min)
            logger.info("Attente du provisioning Supabase...")
            ready = await self._wait_for_supabase_ready(project_id, max_wait=300)

            if not ready:
                raise Exception("Supabase project timeout")

            # Récupérer les détails complets
            details_response = await client.get(
                f"https://api.supabase.com/v1/projects/{project_id}",
                headers={"Authorization": f"Bearer {self.supabase_token}"}
            )

            details = details_response.json()

            # Appliquer le schéma SQL si disponible
            schema = spec.get("plan", {}).get("schema_sql")
            if schema:
                await self._apply_supabase_migrations(project_id, schema)

            return {
                "project_id": project_id,
                "url": f"https://{project['endpoint']}.supabase.co",
                "anon_key": details.get("anon_key", ""),
                "service_key": details.get("service_role_key", ""),
                "db_url": f"postgresql://postgres:{db_password}@{details.get('database', {}).get('host', '')}:5432/postgres",
                "db_password": db_password
            }

    async def _wait_for_supabase_ready(self, project_id: str, max_wait: int = 300) -> bool:
        """Attend que le projet Supabase soit prêt"""
        start = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=30.0) as client:
            while asyncio.get_event_loop().time() - start < max_wait:
                try:
                    response = await client.get(
                        f"https://api.supabase.com/v1/projects/{project_id}",
                        headers={"Authorization": f"Bearer {self.supabase_token}"}
                    )

                    if response.status_code == 200:
                        project = response.json()
                        status = project.get("status", "")

                        if status == "ACTIVE_HEALTHY":
                            return True

                        logger.info(f"Supabase status: {status}")

                except Exception as e:
                    logger.error(f"Erreur vérification Supabase", error=str(e))

                await asyncio.sleep(10)

        return False

    async def _apply_supabase_migrations(self, project_id: str, schema: str):
        """Applique les migrations SQL"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"https://api.supabase.com/v1/projects/{project_id}/database/query",
                    headers={
                        "Authorization": f"Bearer {self.supabase_token}",
                        "Content-Type": "application/json"
                    },
                    json={"query": schema}
                )

                if response.status_code != 200:
                    logger.error(f"Migration failed: {response.text}")
                else:
                    logger.info("Migrations SQL appliquées avec succès")

        except Exception as e:
            logger.error(f"Erreur lors des migrations", error=str(e))

    async def deploy_to_railway(self, spec: Dict, db_config: Dict) -> Dict:
        """Déploie l'application sur Railway"""

        project_name = spec.get("tech_spec", {}).get("project_summary", "project")

        # Créer un nouveau projet Railway
        async with httpx.AsyncClient(timeout=60.0) as client:
            mutation = """
            mutation CreateProject($input: ProjectCreateInput!) {
                projectCreate(input: $input) {
                    id
                    name
                }
            }
            """

            response = await client.post(
                "https://backboard.railway.app/graphql/v2",
                headers={
                    "Authorization": f"Bearer {self.railway_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": mutation,
                    "variables": {
                        "input": {
                            "name": project_name
                        }
                    }
                }
            )

            if response.status_code != 200:
                raise Exception(f"Cannot create Railway project: {response.text}")

            result = response.json()
            project_id = result["data"]["projectCreate"]["id"]

            logger.info(f"Projet Railway créé: {project_id}")

            # Configurer les variables d'environnement
            env_vars = self._prepare_environment_variables(db_config)
            await self._set_railway_env_vars(project_id, env_vars)

            return {
                "project_id": project_id,
                "status": "created",
                "url": f"https://railway.app/project/{project_id}",
                "message": "Projet créé. Connectez votre repo GitHub via Railway UI."
            }

    def _prepare_environment_variables(self, db_config: Dict) -> Dict[str, str]:
        """Prépare les variables d'environnement"""
        env_vars = {}

        if db_config.get("db_url"):
            env_vars["DATABASE_URL"] = db_config["db_url"]
            env_vars["SUPABASE_URL"] = db_config.get("url", "")
            env_vars["SUPABASE_ANON_KEY"] = db_config.get("anon_key", "")
            env_vars["SUPABASE_SERVICE_KEY"] = db_config.get("service_key", "")

        # Générer un secret pour JWT
        env_vars["SECRET_KEY"] = self._generate_secure_password(length=64)

        return env_vars

    async def _set_railway_env_vars(self, project_id: str, env_vars: Dict[str, str]):
        """Configure les variables d'environnement Railway"""
        try:
            mutation = """
            mutation UpsertVariables($input: VariableCollectionUpsertInput!) {
                variableCollectionUpsert(input: $input)
            }
            """

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://backboard.railway.app/graphql/v2",
                    headers={
                        "Authorization": f"Bearer {self.railway_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "query": mutation,
                        "variables": {
                            "input": {
                                "projectId": project_id,
                                "replace": False,
                                "variables": env_vars
                            }
                        }
                    }
                )

                if response.status_code == 200:
                    logger.info("Variables d'environnement configurées")
                else:
                    logger.error(f"Erreur config env vars: {response.text}")

        except Exception as e:
            logger.error(f"Erreur lors de la configuration des env vars", error=str(e))

    def _generate_secure_password(self, length: int = 32) -> str:
        """Génère un mot de passe sécurisé"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def validate_output(self, output: Dict[str, str]) -> List[str]:
        """Valide le résultat du déploiement"""
        errors = []

        if "error" in output:
            errors.append(f"Deployment error: {output['error']}")

        return errors
