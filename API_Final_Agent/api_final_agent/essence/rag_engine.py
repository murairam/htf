"""
RAG Engine - Main entry point
This file provides backward compatibility by importing from the optimized implementation.

DEPRECATED: Direct use of this file is deprecated.
Please use:
  - rag_engine_optimized.OptimizedRAGEngine (recommended for local storage with rate limiting)
  - rag_engine_weaviate.WeaviateRAGEngine (for cloud storage)
"""

import warnings

# Import the optimized version as the default
from .rag_engine_optimized import OptimizedRAGEngine

# Show deprecation warning
warnings.warn(
    "Importing from 'rag_engine' is deprecated. "
    "Please use 'from rag_engine_optimized import OptimizedRAGEngine' instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, expose OptimizedRAGEngine as the default
__all__ = ['OptimizedRAGEngine']
