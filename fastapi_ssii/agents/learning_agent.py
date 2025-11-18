from fastapi_ssii.core.logger import get_logger
from typing import Dict, List, Any
import json
import os
from datetime import datetime

logger = get_logger(__name__)

class LearningAgent:
    """
    Agent d'apprentissage continu qui capture les erreurs et améliore
    les instructions des autres agents pour éviter les mêmes erreurs.
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.error_history_file = "fastapi_ssii/knowledge/error_patterns.json"
        self.improvements_file = "fastapi_ssii/knowledge/agent_improvements.json"
        self.error_patterns = self._load_error_patterns()
        self.agent_improvements = self._load_improvements()

    def _load_error_patterns(self) -> List[Dict]:
        """Charge l'historique des patterns d'erreurs"""
        if os.path.exists(self.error_history_file):
            try:
                with open(self.error_history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur chargement error_patterns", error=str(e))
        return []

    def _load_improvements(self) -> Dict[str, List[str]]:
        """Charge les améliorations suggérées pour chaque agent"""
        if os.path.exists(self.improvements_file):
            try:
                with open(self.improvements_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur chargement improvements", error=str(e))
        return {}

    def _save_error_patterns(self):
        """Sauvegarde les patterns d'erreurs"""
        os.makedirs(os.path.dirname(self.error_history_file), exist_ok=True)
        with open(self.error_history_file, 'w') as f:
            json.dump(self.error_patterns, f, indent=2)

    def _save_improvements(self):
        """Sauvegarde les améliorations"""
        os.makedirs(os.path.dirname(self.improvements_file), exist_ok=True)
        with open(self.improvements_file, 'w') as f:
            json.dump(self.agent_improvements, f, indent=2)

    async def learn_from_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any],
        iteration: int
    ) -> Dict[str, Any]:
        """
        Analyse une erreur et génère des recommandations d'amélioration.

        Args:
            error_type: Type d'erreur (ImportError, ModuleNotFoundError, etc.)
            error_message: Message d'erreur complet
            context: Contexte (fichier, code, agent responsable)
            iteration: Numéro d'itération où l'erreur s'est produite

        Returns:
            Dict avec recommandations et actions
        """
        logger.info(f"📚 LearningAgent analyse l'erreur: {error_type}")

        # Enregistrer l'erreur
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "context": context,
            "iteration": iteration
        }
        self.error_patterns.append(error_record)
        self._save_error_patterns()

        # Vérifier si c'est une erreur récurrente
        similar_errors = self._find_similar_errors(error_type, error_message)

        if len(similar_errors) >= 2:
            logger.info(f"⚠️ Erreur récurrente détectée ({len(similar_errors)} fois)")

            # Analyser et proposer une amélioration permanente
            improvement = await self._generate_improvement(
                error_type,
                error_message,
                similar_errors,
                context
            )

            if improvement:
                agent_name = context.get("agent", "BackendAgent")
                if agent_name not in self.agent_improvements:
                    self.agent_improvements[agent_name] = []

                self.agent_improvements[agent_name].append({
                    "error_pattern": f"{error_type}: {error_message[:100]}",
                    "improvement": improvement,
                    "occurrences": len(similar_errors),
                    "added_at": datetime.now().isoformat()
                })
                self._save_improvements()

                logger.info(f"✅ Amélioration permanente ajoutée pour {agent_name}")

                return {
                    "action": "permanent_improvement",
                    "agent": agent_name,
                    "improvement": improvement,
                    "recurrence_count": len(similar_errors)
                }

        # Si c'est une première occurrence, juste retourner une correction ponctuelle
        return {
            "action": "one_time_fix",
            "recommendation": f"Corriger: {error_type}"
        }

    def _find_similar_errors(self, error_type: str, error_message: str) -> List[Dict]:
        """Trouve des erreurs similaires dans l'historique"""
        similar = []

        # Extraire le pattern clé du message
        key_pattern = self._extract_error_pattern(error_message)

        for error in self.error_patterns:
            if error["type"] == error_type:
                if key_pattern in error["message"]:
                    similar.append(error)

        return similar

    def _extract_error_pattern(self, error_message: str) -> str:
        """Extrait le pattern clé d'un message d'erreur"""
        # Exemples:
        # "ImportError: cannot import name 'UserSchema'" → "cannot import name"
        # "ModuleNotFoundError: No module named 'loguru'" → "No module named"

        patterns = [
            "cannot import name",
            "No module named",
            "missing 1 required",
            "has no attribute",
            "is not a generic class",
            "invalid syntax"
        ]

        for pattern in patterns:
            if pattern in error_message:
                return pattern

        # Si aucun pattern connu, prendre les 50 premiers caractères
        return error_message[:50]

    async def _generate_improvement(
        self,
        error_type: str,
        error_message: str,
        similar_errors: List[Dict],
        context: Dict
    ) -> str:
        """Génère une amélioration permanente via LLM"""

        # Analyser les erreurs similaires
        errors_summary = "\n".join([
            f"- Itération {e['iteration']}: {e['message'][:200]}"
            for e in similar_errors[-5:]  # Dernières 5 occurrences
        ])

        prompt = f"""Tu es un agent d'apprentissage qui améliore les instructions des agents de génération de code.

ERREUR RÉCURRENTE ({len(similar_errors)} occurrences):
Type: {error_type}
Message: {error_message}

HISTORIQUE:
{errors_summary}

CONTEXTE:
Agent: {context.get('agent', 'N/A')}
Fichier: {context.get('file', 'N/A')}

TÂCHE:
Génère une instruction CLAIRE et CONCISE à ajouter aux prompts de l'agent pour éviter cette erreur à l'avenir.

FORMAT DE RÉPONSE (IMPORTANT):
Réponds UNIQUEMENT avec une instruction au format:

"❌ INTERDIT: [ce qu'il ne faut pas faire]
✅ OBLIGATOIRE: [ce qu'il faut faire à la place]
Exemple: [exemple concret]"

IMPORTANT:
- Sois TRÈS spécifique
- Donne un exemple concret
- Utilise le format exact ci-dessus
- Maximum 3-4 lignes
"""

        try:
            improvement = await self.llm_client.generate_with_gemini_async(prompt)
            return improvement.strip()
        except Exception as e:
            logger.error(f"Erreur génération amélioration", error=str(e))
            return ""

    def get_improvements_for_agent(self, agent_name: str) -> List[str]:
        """Récupère toutes les améliorations pour un agent donné"""
        improvements = self.agent_improvements.get(agent_name, [])

        # Retourner les textes d'amélioration
        return [imp["improvement"] for imp in improvements]

    def get_learning_stats(self) -> Dict[str, Any]:
        """Statistiques d'apprentissage"""
        total_errors = len(self.error_patterns)

        error_types = {}
        for error in self.error_patterns:
            error_type = error["type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        total_improvements = sum(len(imps) for imps in self.agent_improvements.values())

        return {
            "total_errors_analyzed": total_errors,
            "error_types": error_types,
            "total_improvements_generated": total_improvements,
            "agents_improved": list(self.agent_improvements.keys())
        }

    async def enhance_agent_prompt(self, agent_name: str, base_prompt: str) -> str:
        """
        Enrichit le prompt d'un agent avec les améliorations apprises.

        Args:
            agent_name: Nom de l'agent (BackendAgent, FrontendAgent, etc.)
            base_prompt: Prompt de base de l'agent

        Returns:
            Prompt enrichi avec les améliorations
        """
        improvements = self.get_improvements_for_agent(agent_name)

        if not improvements:
            return base_prompt

        # Ajouter une section "LEÇONS APPRISES" au prompt
        learned_section = "\n\n🎓 LEÇONS APPRISES (erreurs récurrentes corrigées):\n\n"
        learned_section += "\n\n".join(improvements)

        # Insérer avant la dernière ligne du prompt
        enhanced_prompt = base_prompt + learned_section

        logger.info(f"📚 Prompt enrichi avec {len(improvements)} améliorations pour {agent_name}")

        return enhanced_prompt

    def should_continue_iterations(self, iteration: int, max_time_minutes: int = 30) -> bool:
        """
        Détermine si on doit continuer les itérations.

        Au lieu d'une limite fixe, on utilise:
        - Un timeout global (30 min par défaut)
        - L'analyse des patterns d'erreurs (si on boucle, arrêter)

        Args:
            iteration: Numéro d'itération actuel
            max_time_minutes: Temps maximum en minutes

        Returns:
            True si on doit continuer, False sinon
        """
        # Vérifier si on boucle sur les mêmes erreurs
        if iteration >= 5:
            # Analyser les 5 dernières erreurs
            recent_errors = self.error_patterns[-5:] if len(self.error_patterns) >= 5 else []

            if recent_errors:
                # Extraire les types d'erreurs
                error_types = [e["type"] for e in recent_errors]

                # Si les 5 dernières erreurs sont du même type, on arrête
                if len(set(error_types)) == 1:
                    logger.info(f"⚠️ Boucle détectée sur {error_types[0]}, arrêt des itérations")
                    return False

        # Sinon, continuer (pas de limite d'itérations)
        logger.info(f"✅ Itération {iteration} - Continuation autorisée")
        return True
