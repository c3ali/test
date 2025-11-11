# Guide de Déploiement Automatique

Cette plateforme peut maintenant **générer, déployer et auto-corriger** automatiquement des applications complètes sur Railway et Supabase.

## 🚀 Fonctionnalités

### 1. Génération de Code (Phase 1)
- Analyse du besoin (BusinessAnalystAgent)
- Architecture (ArchitectAgent)
- Code backend Python/FastAPI (BackendAgent)
- Code frontend Vue/React (FrontendAgent)
- Tests (QAAgent)
- Fichiers de déploiement (Dockerfile, requirements.txt, package.json)

### 2. Déploiement Automatique (Phase 2)
- **Supabase**: Création automatique de la base de données PostgreSQL
- **Railway**: Déploiement de l'application avec Docker
- Configuration automatique des variables d'environnement
- Liaison DB ↔ Application

### 3. Auto-Correction (Phase 3)
- Détection automatique des erreurs de déploiement
- Analyse des logs avec patterns regex
- Correction du code via LLM
- Retry automatique (jusqu'à 3 itérations)

## 📋 Prérequis

### Tokens Requis

1. **KIMI_API_KEY** (obligatoire)
   - Pour la génération de code avec Kimi AI
   - Obtenir sur: https://platform.moonshot.cn/

2. **RAILWAY_TOKEN** (optionnel - pour déploiement)
   - Pour déployer l'application
   - Obtenir sur: https://railway.app/account/tokens
   - Cliquer sur "Create Token"

3. **SUPABASE_ACCESS_TOKEN** (optionnel - pour DB)
   - Pour créer la base de données automatiquement
   - Obtenir sur: https://app.supabase.com/account/tokens
   - Cliquer sur "Generate new token"

### Configuration

1. Copier `.env.example` vers `.env`:
```bash
cp .env.example .env
```

2. Remplir les tokens dans `.env`:
```env
# Obligatoire
KIMI_API_KEY=your_kimi_key...

# Pour déploiement automatique (optionnel)
RAILWAY_TOKEN=...
SUPABASE_ACCESS_TOKEN=sbp_...
```

## 🎯 Utilisation

### Mode 1: Génération Uniquement (par défaut)

```bash
curl -X POST http://localhost:8000/generate_project_async \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Une application de gestion de tâches avec authentification",
    "auto_deploy": false
  }'
```

Résultat: Code généré uniquement

### Mode 2: Génération + Déploiement Automatique

```bash
curl -X POST http://localhost:8000/generate_project_async \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Une application de gestion de tâches avec authentification",
    "auto_deploy": true
  }'
```

Résultat:
- ✅ Code généré
- ✅ Base de données Supabase créée et migrée
- ✅ Application déployée sur Railway
- ✅ Variables d'environnement configurées
- ✅ Erreurs auto-corrigées (jusqu'à 3 essais)

## 📊 Réponse API

```json
{
  "status": "accepted",
  "message": "La demande de génération + déploiement automatique a été acceptée.",
  "project_id": "abc123"
}
```

### Vérifier le statut

```bash
curl http://localhost:8000/project_status/abc123
```

Réponse avec déploiement:
```json
{
  "id": "abc123",
  "status": "completed",
  "description": "...",
  "code": {...},
  "plan": {...},
  "deployment": {
    "status": "success",
    "iterations": 1,
    "details": {
      "database": {
        "project_id": "xyz",
        "url": "https://xyz.supabase.co",
        "db_url": "postgresql://..."
      },
      "deployment": {
        "project_id": "railway-id",
        "url": "https://railway.app/project/..."
      }
    }
  }
}
```

## 🔧 Comment ça marche ?

### Pipeline Complet

```
1. 📝 Génération du Code
   └─> BusinessAnalyst → Architect → Backend → Frontend → QA

2. 🗄️ Création Base de Données (si SUPABASE_ACCESS_TOKEN)
   └─> Création projet Supabase
   └─> Application des migrations SQL
   └─> Configuration RLS si nécessaire

3. ☁️ Déploiement (si RAILWAY_TOKEN)
   └─> Création projet Railway
   └─> Configuration env vars (DB_URL, SECRET_KEY, etc.)
   └─> Déploiement Docker

4. 🔧 Auto-Correction (si erreurs)
   └─> Détection erreurs (ImportError, ModuleNotFoundError, etc.)
   └─> Analyse avec regex patterns
   └─> Correction via LLM
   └─> Retry (max 3 fois)
```

### Patterns d'Erreurs Détectés

1. **Module manquant**
   ```
   ModuleNotFoundError: No module named 'loguru'
   → Ajout automatique à requirements.txt
   ```

2. **Erreur de syntaxe**
   ```
   SyntaxError: invalid syntax at line 42
   → Correction via LLM
   ```

3. **Import error**
   ```
   ImportError: cannot import name 'UserSchema' from 'schemas'
   → Correction du nom (UserBase au lieu de UserSchema)
   ```

## 🎛️ Configuration Avancée

### Variables d'environnement générées automatiquement

```env
# Auto-configurées par DeploymentAgent
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
SECRET_KEY=...  # Généré aléatoirement
```

### Limites

- **Max iterations**: 3 essais de correction
- **Timeout Supabase**: 5 minutes pour provisioning
- **Timeout Railway**: 10 minutes pour déploiement

## 🛠️ Développement

### Ajouter un nouveau pattern d'erreur

Modifier `fastapi_ssii/agents/auto_debugger.py`:

```python
# Dans analyze_deployment_error()
new_pattern = re.findall(r"YourError: (.+)", error_msg)
for error in new_pattern:
    bugs.append({
        "type": "your_error_type",
        "error": error
    })
```

### Ajouter une plateforme de déploiement

Créer un nouvel agent dans `fastapi_ssii/agents/` avec:
- Méthode `async def deploy(spec: Dict) -> Dict`
- Gestion des erreurs
- Retour structuré

## 📝 Logs

Les logs JSON structurés sont disponibles dans:
- Console: Logs en temps réel
- Fichiers: (si configuré) logs/deployment.log

Format:
```json
{
  "timestamp": "2025-11-11T10:30:00Z",
  "level": "INFO",
  "message": "Création du projet Supabase...",
  "project_id": "abc123"
}
```

## 🔐 Sécurité

- Les tokens ne sont JAMAIS loggés
- Les mots de passe DB sont générés aléatoirement (32 chars)
- Les secrets JWT sont générés aléatoirement (64 chars)
- Les tokens sont chargés depuis variables d'environnement uniquement

## 🆘 Troubleshooting

### "No RAILWAY_TOKEN found"
→ Ajouter `RAILWAY_TOKEN=...` dans `.env`

### "Supabase project timeout"
→ Attendre plus longtemps ou réessayer (provisioning peut prendre 5+ min)

### "Maximum iterations reached"
→ Vérifier les logs détaillés dans la réponse `deployment.logs`
→ Corriger manuellement le code puis redéployer

## 📚 Ressources

- [Railway Docs](https://docs.railway.app/)
- [Supabase API](https://supabase.com/docs/reference/api/introduction)
- [FastAPI](https://fastapi.tiangolo.com/)
