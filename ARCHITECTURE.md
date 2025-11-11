# Architecture de la Plateforme Autonome

## 🎯 Vue d'Ensemble

Cette plateforme génère, déploie et auto-corrige automatiquement des applications complètes avec une synchronisation parfaite entre GitHub, Supabase et Railway.

## 🔄 Pipeline Orchestré (Ordre CRITIQUE)

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: GÉNÉRATION DU CODE                                 │
│ ├── BusinessAnalystAgent (analyse du besoin)                │
│ ├── ArchitectAgent (plan technique)                         │
│ ├── BackendAgent (code Python avec TOUTES les corrections)  │
│ ├── FrontendAgent (code Vue/React)                          │
│ └── QAAgent (tests)                                         │
│                                                              │
│ ✅ Corrections automatiques intégrées:                       │
│    - Structure fichier unique (models.py, schemas.py)        │
│    - Conventions Pydantic (*Base, *Create, *Response)        │
│    - Prévention imports circulaires (TYPE_CHECKING)          │
│    - Dépendances complètes (loguru, email-validator)         │
│    - Nommage cohérent (setup_cors, pas add_cors_middleware) │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: PUSH GITHUB (DevOpsAgent)                          │
│ ├── Génération nom repo (kebab-case via LLM)                │
│ ├── Création repo GitHub privé                              │
│ ├── Push du code avec git                                   │
│ └── Retourne URL: https://github.com/user/repo              │
│                                                              │
│ ⚠️  CRITIQUE: Railway déploie DEPUIS GitHub, pas local      │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: CRÉATION SUPABASE (DeploymentAgent)                │
│ ├── Création projet Supabase                                │
│ ├── Attente provisioning (max 5min)                         │
│ ├── Application migrations SQL                              │
│ ├── Génération credentials:                                 │
│ │   - DATABASE_URL (PostgreSQL)                             │
│ │   - SUPABASE_URL                                          │
│ │   - SUPABASE_ANON_KEY (clé publique)                      │
│ │   - SUPABASE_SERVICE_KEY (clé privée)                     │
│ └── Retourne toutes les URLs et clés                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: DÉPLOIEMENT RAILWAY (DeploymentAgent)              │
│ ├── Création projet Railway                                 │
│ ├── Configuration env vars avec credentials Supabase        │
│ ├── Génération SECRET_KEY pour JWT                          │
│ ├── Liaison au repo GitHub (Phase 2)                        │
│ └── Déploiement Docker depuis GitHub                        │
│                                                              │
│ 📍 Application LIVE: https://app.railway.app                │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: AUTO-CORRECTION (AutoDebugger)                     │
│ ├── Health check de l'application déployée                  │
│ ├── Analyse logs si erreurs                                 │
│ ├── Détection patterns:                                     │
│ │   - ModuleNotFoundError → Ajout requirements.txt          │
│ │   - Database errors → Vérif migrations                    │
│ │   - Runtime errors → Correction via LLM                   │
│ ├── Correction du code                                      │
│ ├── Re-push GitHub (si nécessaire)                          │
│ ├── Re-deploy Railway                                       │
│ └── Retry jusqu'à 3 fois                                    │
│                                                              │
│ ⚠️  N'intervient QUE sur erreurs de DÉPLOIEMENT             │
│    Ne touche PAS aux corrections structurelles (Phase 1)     │
└─────────────────────────────────────────────────────────────┘
```

## 🛡️ Stratégie de Non-Régression

### Les 10 Corrections Structurelles (Phase 1 - Permanent)

Ces corrections sont **intégrées dans le BackendAgent** et ne doivent **JAMAIS être modifiées** par l'AutoDebugger :

| # | Erreur | Correction | Où |
|---|--------|-----------|-----|
| 1 | `add_cors_middleware` introuvable | Nommage cohérent `setup_cors` | BackendAgent (conventions) |
| 2 | `loguru` manquant | Ajout au mapping | ProjectManager (import_to_package) |
| 3-5 | Structure `models/`, `schemas/` | Fichiers uniques `models.py` | BackendAgent (interdiction absolue) |
| 6 | `email-validator` manquant | Ajout au mapping | ProjectManager (import_to_package) |
| 7 | `*Schema` au lieu de `*Base` | Conventions Pydantic | BackendAgent (conventions) |
| 8 | Imports circulaires | Pattern TYPE_CHECKING | BackendAgent (instructions) |
| 9-10 | `Token`, `TokenRefresh` manquants | Schémas auth obligatoires | BackendAgent (instructions) |

**Ces corrections sont appliquées AVANT le déploiement et ne peuvent PAS régresser.**

### Séparation des Responsabilités

```
BackendAgent
├── Génère le code avec structure correcte
├── Applique les 10 corrections structurelles
└── Code 100% conforme avant push GitHub

AutoDebugger
├── S'occupe UNIQUEMENT des erreurs de déploiement
├── Analyse les logs Railway/Supabase
└── Corrige les bugs runtime (pas la structure)
```

### Garanties de Non-Régression

1. **Génération en 2 phases** : Les fichiers utilitaires sont générés AVANT main.py avec le contexte
2. **Instructions strictes** : Le BackendAgent a des instructions TRÈS détaillées et strictes
3. **Validation** : Les corrections sont appliquées pendant la génération, pas après
4. **Séparation** : L'AutoDebugger ne touche jamais à la structure du code

## 🔗 Synchronisation GitHub ↔ Railway ↔ Supabase

### Ordre d'Exécution

```
1. generate_project()
   └─> Code avec toutes les corrections

2. push_to_github()
   └─> Code versionné et accessible

3. create_supabase()
   └─> DB créée + credentials générés

4. deploy_to_railway()
   ├─> Lié au repo GitHub (étape 2)
   ├─> Env vars avec Supabase (étape 3)
   └─> Déploiement depuis GitHub

5. auto_correction() [si erreurs]
   ├─> Analyse logs Railway
   ├─> Correction bugs runtime
   ├─> Re-push GitHub
   └─> Auto-redeploy Railway
```

### Variables d'Environnement Auto-Configurées

Railway reçoit automatiquement :

```env
# Supabase (depuis Phase 3)
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Sécurité (généré)
SECRET_KEY=<64 chars aléatoires>

# Application
PORT=8080  # Railway auto
```

## 🧪 Tests de Non-Régression

### Avant chaque déploiement

Le code généré doit respecter :

- ✅ Structure fichier unique (`models.py`, `schemas.py`)
- ✅ Conventions Pydantic (`*Base`, `*Create`, `*Response`)
- ✅ Pas d'imports circulaires
- ✅ Toutes les dépendances présentes
- ✅ Nommage cohérent des fonctions
- ✅ Schémas auth complets

### Si erreur détectée

1. Vérifier si c'est une **erreur de structure** (Phase 1) ou **erreur de déploiement** (Phase 5)
2. Si structure → **BUG dans BackendAgent** (à corriger là-bas)
3. Si déploiement → AutoDebugger s'en occupe

## 📊 Flux de Données

```
User Input
    ↓
description: "Une app de gestion de tâches"
    ↓
┌─────────────────┐
│ Orchestrator    │ ← Coordonne tout
└─────────────────┘
    ↓
┌─────────────────┐
│ BackendAgent    │ ← Génère code avec corrections
└─────────────────┘
    ↓
code: {
  "models.py": "...",      ← Fichier unique ✅
  "schemas.py": "...",     ← *Base, *Create, *Response ✅
  "main.py": "...",        ← setup_cors() ✅
  "requirements.txt": "..." ← loguru, email-validator ✅
}
    ↓
┌─────────────────┐
│ DevOpsAgent     │ ← Push GitHub
└─────────────────┘
    ↓
github_url: "https://github.com/user/repo"
    ↓
┌─────────────────┐
│ DeploymentAgent │ ← Supabase + Railway
└─────────────────┘
    ↓
deployment: {
  "database": {
    "url": "https://xyz.supabase.co",
    "db_url": "postgresql://...",
    "anon_key": "...",
    "service_key": "..."
  },
  "app": {
    "url": "https://app.railway.app"
  }
}
    ↓
┌─────────────────┐
│ AutoDebugger    │ ← Vérifie et corrige runtime
└─────────────────┘
    ↓
status: "success" | "failed"
```

## 🔐 Sécurité

- **Tokens jamais loggés** : RAILWAY_TOKEN, SUPABASE_ACCESS_TOKEN masqués
- **Secrets générés** : PASSWORD (32 chars), SECRET_KEY (64 chars)
- **Repos privés** : GitHub repos créés en mode privé par défaut
- **Env vars sécurisées** : Configurées dans Railway, jamais en clair dans le code

## 📝 Logs Structurés

Format JSON pour chaque étape :

```json
{
  "timestamp": "2025-11-11T10:30:00Z",
  "level": "INFO",
  "agent": "Orchestrator",
  "phase": "2/5",
  "message": "Push du code vers GitHub",
  "project_id": "abc123",
  "github_url": "https://github.com/user/repo"
}
```

## 🚦 État du Déploiement

### Success

```json
{
  "status": "success",
  "message": "Déploiement complet avec synchronisation GitHub → Supabase → Railway",
  "details": {
    "github": {"url": "..."},
    "database": {"url": "...", "db_url": "..."},
    "deployment": {"url": "..."}
  }
}
```

### Failed

```json
{
  "status": "failed",
  "error": "...",
  "details": {
    "github": {"url": "..."},
    "database": null,
    "deployment": null
  }
}
```

## 🔄 Évolution Future

- [ ] Support Vercel pour le frontend
- [ ] Support Netlify
- [ ] Support AWS Lambda
- [ ] Tests E2E automatiques
- [ ] Monitoring post-déploiement
- [ ] Rollback automatique si échec
