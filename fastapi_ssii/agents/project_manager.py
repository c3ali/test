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

    def _scan_imports_from_code(self, code_files: dict) -> list:
        """
        Scanne le code généré pour détecter les imports et mapper aux packages pip.
        """
        import re

        # Mapping des imports vers les packages pip
        import_to_package = {
            'psycopg2': 'psycopg2-binary',
            'pymysql': 'pymysql',
            'sqlalchemy': 'sqlalchemy',
            'redis': 'redis',
            'celery': 'celery',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'requests': 'requests',
            'aiohttp': 'aiohttp',
            'jwt': 'PyJWT',
            'bcrypt': 'bcrypt',
            'passlib': 'passlib',
            'pydantic': 'pydantic',
            'jinja2': 'jinja2',
            'PIL': 'Pillow',
            'cv2': 'opencv-python',
            'matplotlib': 'matplotlib',
            'bs4': 'beautifulsoup4',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv',
        }

        detected_packages = set()

        # Scanner tous les fichiers Python générés
        for filename, code in code_files.items():
            if not filename.endswith('.py'):
                continue

            # Trouver tous les imports
            # Pattern pour: import X, from X import Y
            import_patterns = [
                r'^\s*import\s+([a-zA-Z0-9_]+)',
                r'^\s*from\s+([a-zA-Z0-9_]+)',
            ]

            for line in code.split('\n'):
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        module_name = match.group(1)
                        # Mapper au package pip si connu
                        if module_name in import_to_package:
                            detected_packages.add(import_to_package[module_name])
                            logger.info(f"Détecté dépendance: {import_to_package[module_name]} (import {module_name})")

        return list(detected_packages)

    def _generate_deployment_files(self, plan: dict, tech_spec: dict, generated_code: dict = None) -> dict:
        """
        Génère les fichiers de configuration nécessaires pour le déploiement.
        """
        deployment_files = {}

        # 1. runtime.txt pour spécifier la version Python (éviter Python 3.13)
        runtime_content = "python-3.12.0"
        deployment_files["runtime.txt"] = runtime_content
        logger.info("Généré runtime.txt avec Python 3.12.0")

        # 2. requirements.txt pour Python/FastAPI
        dependencies = plan.get("dependencies", [])

        # Scanner le code généré pour détecter les imports manquants
        if generated_code:
            detected_deps = self._scan_imports_from_code(generated_code)
            # Ajouter les dépendances détectées si pas déjà présentes
            for dep in detected_deps:
                dep_name = dep.split('>=')[0].split('==')[0]  # Extraire le nom sans version
                if not any(dep_name in d for d in dependencies):
                    dependencies.append(dep)
                    logger.info(f"Ajout automatique de la dépendance détectée: {dep}")

        if dependencies:
            # S'assurer que les dépendances de base FastAPI sont présentes avec versions compatibles
            essential_deps = {
                "fastapi": "fastapi>=0.109.0",
                "uvicorn": "uvicorn[standard]>=0.27.0",
                "python-dotenv": "python-dotenv>=1.0.0",
                "pydantic": "pydantic>=2.6.0"  # Version compatible avec Python 3.12
            }

            # Ajouter les dépendances essentielles si absentes
            for key, value in essential_deps.items():
                if not any(key in d for d in dependencies):
                    dependencies.append(value)
                else:
                    # Remplacer si version non spécifiée
                    for i, dep in enumerate(dependencies):
                        if dep == key:
                            dependencies[i] = value

            deployment_files["requirements.txt"] = "\n".join(dependencies)
            logger.info(f"Généré requirements.txt avec {len(dependencies)} dépendances")

        # 3. Procfile pour Railway/Heroku
        # Déterminer le fichier d'entrée (main.py, app.py, etc.)
        entry_file = None
        for filename in plan.get("files", {}).keys():
            if filename in ["main.py", "app.py", "server.py"]:
                entry_file = filename
                break

        if not entry_file and any(f.endswith(".py") for f in plan.get("files", {}).keys()):
            # Prendre le premier fichier Python
            entry_file = next(f for f in plan.get("files", {}).keys() if f.endswith(".py"))

        if entry_file:
            module_name = entry_file[:-3]  # Enlever .py
            procfile_content = f"web: uvicorn {module_name}:app --host 0.0.0.0 --port $PORT"
            deployment_files["Procfile"] = procfile_content
            logger.info(f"Généré Procfile avec point d'entrée: {module_name}:app")

        # 4. package.json si frontend détecté
        has_frontend = any(f.endswith((".html", ".css", ".js", ".vue", ".jsx", ".tsx"))
                          for f in plan.get("files", {}).keys())

        if has_frontend:
            package_json = {
                "name": tech_spec.get("project_summary", "project").lower().replace(" ", "-"),
                "version": "1.0.0",
                "description": tech_spec.get("project_summary", "Generated project"),
                "scripts": {
                    "dev": "vite",
                    "build": "vite build",
                    "preview": "vite preview"
                },
                "dependencies": {
                    "vue": "^3.3.0" if any(".vue" in f for f in plan.get("files", {})) else None,
                    "react": "^18.2.0" if any(".jsx" in f or ".tsx" in f for f in plan.get("files", {})) else None,
                },
                "devDependencies": {
                    "vite": "^5.0.0"
                }
            }
            # Nettoyer les None
            package_json["dependencies"] = {k: v for k, v in package_json["dependencies"].items() if v}

            import json
            deployment_files["package.json"] = json.dumps(package_json, indent=2)
            logger.info("Généré package.json pour le frontend")

        # 5. .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
npm-debug.log
yarn-error.log

# Build
dist/
build/
"""
        deployment_files[".gitignore"] = gitignore_content
        logger.info("Généré .gitignore")

        # 6. README.md
        readme_content = f"""# {tech_spec.get('project_summary', 'Project')}

## Description
{tech_spec.get('project_summary', 'A generated project')}

## Features
{chr(10).join(f"- {feature}" for feature in tech_spec.get('main_features', []))}

## Installation

### Backend (Python/FastAPI)
```bash
pip install -r requirements.txt
```

### Frontend (if applicable)
```bash
npm install
```

## Running the Application

### Development
```bash
# Backend
uvicorn main:app --reload

# Frontend (if applicable)
npm run dev
```

### Production (Railway)
The application is configured to deploy automatically on Railway using the Procfile.

## Environment Variables
Create a `.env` file with necessary environment variables (database URL, API keys, etc.)

## Project Structure
{chr(10).join(f"- `{filename}`: {description}" for filename, description in list(plan.get('files', {}).items())[:10])}
"""
        deployment_files["README.md"] = readme_content
        logger.info("Généré README.md")

        return deployment_files

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

        logger.info("Phase 5: Deployment Configuration")
        # Rassembler le code généré pour la détection des dépendances
        all_generated_code = {**backend_code, **frontend_code, **tests}
        deployment_files = self._generate_deployment_files(plan, tech_spec, all_generated_code)

        logger.info("Phase 6: Assembly")
        full_code = {**backend_code, **frontend_code, **tests, **deployment_files}

        return {
            "message": "Project generated successfully!",
            "code": full_code,
            "plan": plan,
            "tech_spec": tech_spec
        }

orchestrator = Orchestrator(gemini_client)
