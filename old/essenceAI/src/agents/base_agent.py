"""
Base Agent Class
Abstract base class for all agents in the essenceAI system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Provides common functionality and interface for specialized agents.
    """

    def __init__(self, name: str, description: str, llm_provider: Optional[str] = None):
        """
        Initialize the base agent.

        Args:
            name: Agent name
            description: Agent description/purpose
            llm_provider: LLM provider to use ('openai' or 'anthropic')
        """
        self.name = name
        self.description = description
        self.llm_provider = llm_provider or os.getenv("LLM_PROVIDER", "openai").lower()
        self.history: List[Dict[str, Any]] = []
        self.created_at = datetime.now()

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task. Must be implemented by subclasses.

        Args:
            task: Task parameters as a dictionary

        Returns:
            Result dictionary with status, data, and metadata
        """
        pass

    def log_action(self, action: str, details: Dict[str, Any]):
        """
        Log an action to the agent's history.

        Args:
            action: Action name
            details: Action details
        """
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        })

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the agent's action history."""
        return self.history

    def clear_history(self):
        """Clear the agent's action history."""
        self.history = []

    def get_status(self) -> Dict[str, Any]:
        """
        Get the agent's current status.

        Returns:
            Status dictionary with agent metadata
        """
        return {
            'name': self.name,
            'description': self.description,
            'llm_provider': self.llm_provider,
            'created_at': self.created_at.isoformat(),
            'actions_count': len(self.history)
        }

    def _create_success_response(self, data: Any, message: str = "Task completed successfully") -> Dict[str, Any]:
        """
        Create a standardized success response.

        Args:
            data: Result data
            message: Success message

        Returns:
            Standardized response dictionary
        """
        return {
            'status': 'success',
            'agent': self.name,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

    def _create_error_response(self, error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a standardized error response.

        Args:
            error: Error message
            details: Additional error details

        Returns:
            Standardized error response dictionary
        """
        return {
            'status': 'error',
            'agent': self.name,
            'error': error,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', actions={len(self.history)})"
