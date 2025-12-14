"""
Base RAG Engine - Shared functionality for all RAG implementations
Eliminates code duplication across different RAG engine types
"""

import os
import hashlib
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter

# Load environment variables
load_dotenv()

# Import logger
from logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class BaseRAGEngine:
    """
    Base class for RAG engines with shared caching and utility methods.
    Subclasses implement specific storage backends (local, Weaviate, etc.)
    """

    def __init__(self, data_dir: str = "data", persist_dir: str = ".storage", cache_dir: str = ".cache"):
        """
        Initialize base RAG engine.
        
        Args:
            data_dir: Directory containing source documents
            persist_dir: Directory for persisting index (if applicable)
            cache_dir: Directory for query cache
        """
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        self.index = None
        self.query_engine = None

        # Query cache to avoid repeated API calls
        self.query_cache = {}
        self._load_query_cache()

    def _load_query_cache(self):
        """Load cached queries from disk."""
        cache_file = self.cache_dir / "query_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.query_cache = json.load(f)
                logger.info(f"Loaded {len(self.query_cache)} cached queries from disk")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse query cache JSON: {e}")
                self.query_cache = {}
            except IOError as e:
                logger.error(f"Failed to read query cache file: {e}")
                self.query_cache = {}

    def _save_query_cache(self):
        """Save query cache to disk."""
        cache_file = self.cache_dir / "query_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.query_cache, f, indent=2)
            logger.debug(f"Saved {len(self.query_cache)} queries to cache")
        except IOError as e:
            logger.error(f"Failed to save query cache: {e}")

    def _get_query_hash(self, query: str, product_context: Optional[str] = None) -> str:
        """
        Generate hash for query caching with product context.

        Args:
            query: The query string
            product_context: Optional product description to make cache product-specific

        Returns:
            Hash string for caching
        """
        # Include product context in hash to ensure different products get different results
        cache_key = query
        if product_context:
            cache_key = f"{product_context}||{query}"
        return hashlib.md5(cache_key.encode()).hexdigest()

    def _setup_base_llm(self, model: str = "gpt-4o-mini", temperature: float = 0.1):
        """
        Configure base LLM settings (shared across all implementations).
        
        Args:
            model: OpenAI model to use
            temperature: LLM temperature setting
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Use GPT-4o-mini for cost-effective queries
        Settings.llm = OpenAI(
            model=model,
            api_key=api_key,
            temperature=temperature
        )

        logger.info(f"✓ LLM configured: {model} (temperature: {temperature})")

    def _setup_base_node_parser(self, chunk_size: int = 300, chunk_overlap: int = 30):
        """
        Configure base node parser settings.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        Settings.node_parser = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        logger.info(f"✓ Node parser configured: chunk_size={chunk_size}, overlap={chunk_overlap}")

    def get_citations(self, response) -> List[Dict]:
        """
        Extract citations from a response object.

        Args:
            response: Query response object

        Returns:
            List of citation dictionaries
        """
        citations = []
        if hasattr(response, 'source_nodes'):
            for i, node in enumerate(response.source_nodes):
                metadata = node.node.metadata if hasattr(node.node, 'metadata') else {}
                file_name = metadata.get('file_name', 'Unknown')
                if file_name != 'Unknown':
                    file_name = Path(file_name).stem

                citation = {
                    "source_id": i + 1,
                    "file_name": file_name,
                    "page": metadata.get('page_label', 'N/A'),
                    "relevance_score": round(node.score, 3) if hasattr(node, 'score') else None,
                    "excerpt": node.node.text[:200] + "..." if len(node.node.text) > 200 else node.node.text
                }
                citations.append(citation)
        return citations

    def get_cited_answer(
        self, 
        query: str, 
        use_cache: bool = False, 
        product_context: Optional[str] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Query with optional caching to avoid repeated API calls.

        Args:
            query: The query string
            use_cache: Whether to use cached results (default False for dynamic queries)
            product_context: Product description to make cache product-specific

        Returns:
            Tuple of (answer, citations)
        """
        if not self.query_engine:
            raise RuntimeError("Index not initialized. Call initialize_index() first.")

        # Check cache first (with product context)
        query_hash = self._get_query_hash(query, product_context)
        if use_cache and query_hash in self.query_cache:
            logger.info("Cache hit: Using cached query result (no API call)")
            cached = self.query_cache[query_hash]
            return cached['answer'], cached['citations']

        try:
            # Make API call
            response = self.query_engine.query(query)
            answer = str(response)

            # Extract citations
            citations = self.get_citations(response)

            # Cache the result
            self.query_cache[query_hash] = {
                'answer': answer,
                'citations': citations
            }
            self._save_query_cache()

            return answer, citations

        except (ConnectionError, TimeoutError) as e:
            logger.error(f"API connection error during query: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid query or response format: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during query: {e}", exc_info=True)
            raise

    def query(self, query_str: str):
        """
        Query the index and return a response object.
        This method provides compatibility with different interfaces.

        Args:
            query_str: The question to ask

        Returns:
            Response object with .response attribute and .source_nodes
        """
        if not self.query_engine:
            raise RuntimeError("Index not initialized. Call initialize_index() first.")

        return self.query_engine.query(query_str)

    def clear_cache(self):
        """Clear query cache to force fresh API calls."""
        cache_size = len(self.query_cache)
        self.query_cache = {}
        self._save_query_cache()
        logger.info(f"Query cache cleared ({cache_size} entries removed)")

    # High-level query methods (shared across all implementations)

    def get_marketing_strategy(
        self,
        product_concept: str,
        category: str,
        target_segment: str = "Skeptic",
        use_cache: bool = False
    ) -> Tuple[str, List[Dict]]:
        """
        Get marketing strategy with product-specific results.

        Args:
            product_concept: The product to analyze
            category: Product category
            target_segment: Target consumer segment
            use_cache: Whether to use cached results
        """
        query = f"""Based on research about {category} and {target_segment} consumers:

Product: {product_concept}

Provide a concise marketing strategy (3-4 key points) addressing:
1. Key psychological factors for this segment
2. Recommended messaging approach
3. What to avoid

Cite specific research findings."""

        return self.get_cited_answer(query, use_cache=use_cache, product_context=product_concept)

    def get_segment_strategy(
        self,
        product_concept: str,
        target_segment: str,
        use_cache: bool = False
    ) -> Tuple[str, List[Dict]]:
        """
        Get segment-specific strategy without category filter.

        Args:
            product_concept: The product to analyze
            target_segment: Target consumer segment
            use_cache: Whether to use cached results
        """
        query = f"""Based on research about {target_segment} consumers and sustainable food:

Product: {product_concept}

Provide a concise marketing strategy (3-4 key points) addressing:
1. Key psychological factors for this segment
2. Recommended messaging approach
3. What to avoid

Cite specific research findings."""

        return self.get_cited_answer(query, use_cache=use_cache, product_context=product_concept)

    def get_general_strategy(
        self,
        product_concept: str,
        category: str,
        use_cache: bool = False
    ) -> Tuple[str, List[Dict]]:
        """
        Get category-specific strategy for general audience.

        Args:
            product_concept: The product to analyze
            category: Product category
            use_cache: Whether to use cached results
        """
        query = f"""Based on research about {category} products:

Product: {product_concept}

Provide a general marketing strategy (3-4 key points) addressing:
1. Key consumer acceptance factors
2. Recommended messaging approach
3. Common barriers to address

Cite specific research findings."""

        return self.get_cited_answer(query, use_cache=use_cache, product_context=product_concept)

    def get_universal_strategy(
        self,
        product_concept: str,
        use_cache: bool = False
    ) -> Tuple[str, List[Dict]]:
        """
        Get universal strategy for sustainable food products.

        Args:
            product_concept: The product to analyze
            use_cache: Whether to use cached results
        """
        query = f"""Based on research about sustainable food alternatives:

Product: {product_concept}

Provide a universal marketing strategy (3-4 key points) addressing:
1. General consumer acceptance factors
2. Recommended messaging approach
3. Common barriers across all sustainable food categories

Cite specific research findings."""

        return self.get_cited_answer(query, use_cache=use_cache, product_context=product_concept)

    def get_consumer_insights(
        self, 
        category: str, 
        product_context: Optional[str] = None, 
        use_cache: bool = False
    ) -> Tuple[str, List[Dict]]:
        """
        Get consumer insights with optional product context.

        Args:
            category: Product category
            product_context: Optional product description for context
            use_cache: Whether to use cached results
        """
        query = f"""Summarize key consumer acceptance factors for {category} products:
- Main barriers
- Success factors
- Role of familiarity"""

        if product_context:
            query += f"\n\nSpecific product context: {product_context}"

        return self.get_cited_answer(query, use_cache=use_cache, product_context=product_context)

    # Abstract methods to be implemented by subclasses

    def initialize_index(self, force_reload: bool = False) -> bool:
        """
        Initialize or load the vector index.
        Must be implemented by subclasses.
        
        Args:
            force_reload: Force rebuilding the index
            
        Returns:
            True if successful
        """
        raise NotImplementedError("Subclasses must implement initialize_index()")

    def _setup_embeddings(self):
        """
        Configure embedding model.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _setup_embeddings()")
