# fastapi_ssii/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    def __init__(self, name: str, llm_client):
        self.name = name
        self.llm_client = llm_client
        self.context = {}
        self.dependencies = []

    @abstractmethod
    async def generate(self, specification: Dict[str, Any]) -> Dict[str, str]:
        """Méthode à implémenter par chaque agent"""
        pass

    @abstractmethod
    def validate_output(self, output: Dict[str, str]) -> List[str]:
        """Valide la sortie de l'agent"""
        pass

    def set_context(self, context: Dict[str, Any]):
        """Partage le contexte entre agents"""
        self.context = context

    def add_dependency(self, agent_name: str):
        """Déclare les dépendances entre agents"""
        self.dependencies.append(agent_name)
