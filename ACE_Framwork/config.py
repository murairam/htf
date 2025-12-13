"""
Configuration settings for the ACE Plant-Based Packaging Intelligence System.
"""
import os
from dataclasses import dataclass, field
from typing import Optional

# Environment variables for API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENFOODFACTS_USER_AGENT = os.getenv("OPENFOODFACTS_USER_AGENT", "PlantBasedIntelligence/1.0")

# Default paths
DEFAULT_PLAYBOOK_PATH = "playbook.json"
DEFAULT_LOG_PATH = "logs"


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str = "openai"
    model: str = "gpt-4"
    vision_model: str = "gpt-4o"  # For image analysis
    temperature: float = 0.0
    max_tokens: int = 4096
    stream: bool = True
    api_key: Optional[str] = None
    
    def __post_init__(self):
        if self.api_key is None:
            if self.provider == "openai":
                self.api_key = OPENAI_API_KEY
            elif self.provider == "google":
                self.api_key = GOOGLE_API_KEY
            elif self.provider == "anthropic":
                self.api_key = ANTHROPIC_API_KEY


@dataclass
class PlaybookConfig:
    """Configuration for playbook management."""
    path: str = DEFAULT_PLAYBOOK_PATH
    max_bullets_per_section: int = 100
    dedup_similarity_threshold: float = 0.85
    enable_semantic_dedup: bool = True


@dataclass
class ACEConfig:
    """Main configuration for the ACE Plant-Based Packaging Intelligence system."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    playbook: PlaybookConfig = field(default_factory=PlaybookConfig)
    max_reflector_iterations: int = 3
    enable_streaming: bool = True
    log_path: str = DEFAULT_LOG_PATH
    verbose: bool = True


# Playbook section names for Plant-Based Intelligence domain
PLAYBOOK_SECTIONS = [
    "scoring_rules",
    "plant_based_heuristics",
    "ultra_processing_pitfalls",
    "packaging_patterns",
    "go_to_market_rules"
]

# Section prefixes for bullet IDs
SECTION_PREFIXES = {
    "scoring_rules": "sr",
    "plant_based_heuristics": "pbh",
    "ultra_processing_pitfalls": "upp",
    "packaging_patterns": "pkg",
    "go_to_market_rules": "gtm"
}

# Plant-based category mapping from OpenFoodFacts categories
PLANT_BASED_CATEGORIES = [
    "plant-based",
    "vegan",
    "vegetarian",
    "meat-alternatives",
    "dairy-alternatives",
    "plant-milks",
    "tofu",
    "tempeh",
    "seitan",
    "legumes",
    "plant-proteins"
]