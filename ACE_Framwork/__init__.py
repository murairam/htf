"""
ACE Product Intelligence System

Agentic Context Engineering for Product Analysis and Marketing Intelligence.
"""

__version__ = "1.0.0"

from config import ACEConfig, LLMConfig, PlaybookConfig
from playbook import Playbook, PlaybookManager, Bullet
from agents import (
    ACEPipeline,
    Generator,
    Reflector,
    Curator,
    GeneratorOutput,
    ReflectorOutput,
    CuratorOutput
)
from product_data import (
    ProductData,
    ImageAnalysisResult,
    OpenFoodFactsClient,
    ImageAnalyzer
)

__all__ = [
    "ACEConfig", "LLMConfig", "PlaybookConfig",
    "Playbook", "PlaybookManager", "Bullet",
    "ACEPipeline", "Generator", "Reflector", "Curator",
    "GeneratorOutput", "ReflectorOutput", "CuratorOutput",
    "ProductData", "ImageAnalysisResult", "OpenFoodFactsClient", "ImageAnalyzer"
]
