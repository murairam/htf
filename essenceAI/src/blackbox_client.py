"""
Blackbox AI API Client
Provides interface to Blackbox AI for code generation and technical tasks
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Import logger
from logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class BlackboxAIClient:
    """
    Client for interacting with Blackbox AI API.
    Supports code generation, technical analysis, and task automation.
    """

    def __init__(
        self,
        chat_api_key: Optional[str] = None,
        task_api_key: Optional[str] = None,
        cache_dir: str = ".cache"
    ):
        """
        Initialize Blackbox AI client with support for both key types.

        Args:
            chat_api_key: sk- key for chat completions (defaults to BLACKBOX_CHAT_API_KEY env var)
            task_api_key: bb- key for repository tasks (defaults to BLACKBOX_TASK_API_KEY env var)
            cache_dir: Directory for caching responses
        """
        # Support both key types
        self.chat_api_key = chat_api_key or os.getenv("BLACKBOX_CHAT_API_KEY") or os.getenv("BLACKBOX_API_KEY")
        self.task_api_key = task_api_key or os.getenv("BLACKBOX_TASK_API_KEY") or os.getenv("BLACKBOX_API_KEY")

        if not self.chat_api_key and not self.task_api_key:
            logger.warning("No Blackbox AI API keys found in environment")

        # Different base URLs for different APIs
        self.chat_base_url = "https://api.blackbox.ai"
        self.task_base_url = "https://cloud.blackbox.ai"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Query cache
        self.query_cache = {}
        self._load_cache()

        # Track API usage
        self.api_calls_made = 0
        self.cache_hits = 0

        # Log key availability
        if self.chat_api_key:
            key_type = "sk-" if self.chat_api_key.startswith("sk-") else "bb_"
            logger.info(f"Chat API key loaded ({key_type}...)")
        if self.task_api_key:
            key_type = "sk-" if self.task_api_key.startswith("sk-") else "bb_"
            logger.info(f"Task API key loaded ({key_type}...)")

    def _load_cache(self):
        """Load cached responses from disk."""
        cache_file = self.cache_dir / "blackbox_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.query_cache = json.load(f)
                logger.info(f"Loaded {len(self.query_cache)} cached Blackbox queries")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load Blackbox cache: {e}")
                self.query_cache = {}

    def _save_cache(self):
        """Save query cache to disk."""
        cache_file = self.cache_dir / "blackbox_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.query_cache, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save Blackbox cache: {e}")

    def _get_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key for request."""
        cache_str = f"{prompt}|{model}|{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(cache_str.encode()).hexdigest()

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "blackbox",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Blackbox AI.
        Requires sk- API key (paid subscription).

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (blackbox, blackboxai/openai/gpt-4, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            use_cache: Whether to use cached responses
            **kwargs: Additional API parameters

        Returns:
            API response dictionary
        """
        if not self.chat_api_key:
            raise ValueError(
                "Chat API key not configured. "
                "Requires sk- key (paid subscription). "
                "Set BLACKBOX_CHAT_API_KEY environment variable."
            )

        # Create cache key from last user message
        user_messages = [m for m in messages if m.get('role') == 'user']
        if user_messages and use_cache:
            cache_key = self._get_cache_key(
                user_messages[-1]['content'],
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            if cache_key in self.query_cache:
                self.cache_hits += 1
                logger.info("Cache hit: Using cached Blackbox response")
                return self.query_cache[cache_key]

        # Make API request
        self.api_calls_made += 1

        headers = {
            "Authorization": f"Bearer {self.chat_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            **kwargs
        }

        try:
            response = requests.post(
                f"{self.chat_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            # Cache the result
            if use_cache and user_messages:
                self.query_cache[cache_key] = result
                self._save_cache()

            logger.info(f"Blackbox API call successful (model: {model})")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Blackbox API request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Blackbox API response: {e}")
            raise

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        use_cache: bool = True
    ) -> str:
        """
        Generate code using Blackbox AI.

        Args:
            prompt: Code generation prompt
            language: Programming language
            use_cache: Whether to use cached responses

        Returns:
            Generated code as string
        """
        messages = [
            {
                "role": "system",
                "content": f"You are an expert {language} programmer. Generate clean, efficient, well-documented code."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            response = self.chat_completion(
                messages=messages,
                model="blackbox-code",
                temperature=0.1,
                use_cache=use_cache
            )

            # Extract code from response
            content = response['choices'][0]['message']['content']

            # Remove markdown code blocks if present
            if "```" in content:
                # Extract code between ``` markers
                parts = content.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Odd indices are code blocks
                        # Remove language identifier if present
                        lines = part.strip().split('\n')
                        if lines[0].strip().lower() in ['python', 'javascript', 'java', 'cpp', 'c++', 'go', 'rust']:
                            return '\n'.join(lines[1:])
                        return part.strip()

            return content.strip()

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise

    def analyze_code(
        self,
        code: str,
        task: str = "review",
        use_cache: bool = True
    ) -> str:
        """
        Analyze code using Blackbox AI.

        Args:
            code: Code to analyze
            task: Analysis task (review, optimize, debug, explain)
            use_cache: Whether to use cached responses

        Returns:
            Analysis result as string
        """
        task_prompts = {
            "review": "Review this code for best practices, potential bugs, and improvements:",
            "optimize": "Suggest optimizations for this code:",
            "debug": "Help debug this code and identify potential issues:",
            "explain": "Explain what this code does in detail:"
        }

        prompt = task_prompts.get(task, task_prompts["review"])

        messages = [
            {
                "role": "system",
                "content": "You are an expert code reviewer and software engineer."
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n```\n{code}\n```"
            }
        ]

        try:
            response = self.chat_completion(
                messages=messages,
                model="blackbox-code",
                temperature=0.1,
                use_cache=use_cache
            )

            return response['choices'][0]['message']['content']

        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            raise

    def process_data(
        self,
        data: Any,
        task: str,
        use_cache: bool = True
    ) -> str:
        """
        Process data using Blackbox AI.

        Args:
            data: Data to process (will be converted to string)
            task: Processing task description
            use_cache: Whether to use cached responses

        Returns:
            Processing result as string
        """
        messages = [
            {
                "role": "system",
                "content": "You are a data processing expert. Analyze and transform data as requested."
            },
            {
                "role": "user",
                "content": f"{task}\n\nData:\n{json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)}"
            }
        ]

        try:
            response = self.chat_completion(
                messages=messages,
                model="blackbox",
                temperature=0.1,
                use_cache=use_cache
            )

            return response['choices'][0]['message']['content']

        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        total_requests = self.api_calls_made + self.cache_hits
        cache_efficiency = (self.cache_hits / max(total_requests, 1)) * 100

        return {
            'api_calls_made': self.api_calls_made,
            'cache_hits': self.cache_hits,
            'cache_efficiency': f"{cache_efficiency:.1f}%",
            'cached_queries': len(self.query_cache)
        }

    def create_repository_task(
        self,
        prompt: str,
        repo_url: str,
        branch: str = "main",
        agent: str = "blackbox",
        model: str = "blackboxai/blackbox-pro",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a repository task using Blackbox AI.
        Works with both bb_ and sk- keys.

        Args:
            prompt: Task description
            repo_url: GitHub repository URL
            branch: Branch to work on
            agent: Agent to use (blackbox, claude-code, codex, gemini)
            model: Model to use
            **kwargs: Additional task parameters

        Returns:
            Task creation response
        """
        if not self.task_api_key:
            raise ValueError(
                "Task API key not configured. "
                "Set BLACKBOX_TASK_API_KEY or BLACKBOX_API_KEY environment variable."
            )

        headers = {
            "Authorization": f"Bearer {self.task_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt,
            "repoUrl": repo_url,
            "selectedBranch": branch,
            "selectedAgent": agent,
            "selectedModel": model,
            **kwargs
        }

        try:
            response = requests.post(
                f"{self.task_base_url}/api/tasks",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Repository task created: {result.get('task', {}).get('id', 'N/A')}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Repository task creation failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse task response: {e}")
            raise

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a repository task.

        Args:
            task_id: Task ID to check

        Returns:
            Task status response
        """
        if not self.task_api_key:
            raise ValueError("Task API key not configured")

        headers = {
            "Authorization": f"Bearer {self.task_api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(
                f"{self.task_base_url}/api/tasks/{task_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get task status: {e}")
            raise

    def clear_cache(self):
        """Clear query cache."""
        cache_size = len(self.query_cache)
        self.query_cache = {}
        self._save_cache()
        logger.info(f"Blackbox cache cleared ({cache_size} entries removed)")


# Convenience function for quick access
def get_blackbox_client() -> BlackboxAIClient:
    """Get a configured Blackbox AI client instance."""
    return BlackboxAIClient()
