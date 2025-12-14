"""
Weaviate-based RAG Engine
Uses Weaviate Cloud as vector store - embeddings are stored remotely
This eliminates the need to rebuild embeddings every time!
Inherits shared functionality from BaseRAGEngine
"""

import os
import time
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.weaviate import WeaviateVectorStore

# Import base class
from rag_engine_base import BaseRAGEngine

# Import logger
from logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class WeaviateRAGEngine(BaseRAGEngine):
    """
    RAG engine using Weaviate Cloud for vector storage.
    Embeddings are stored in Weaviate, so you only pay once!
    """

    def __init__(
        self,
        data_dir: str = "data",
        persist_dir: str = ".storage",  # Not used but kept for compatibility
        cache_dir: str = ".cache",
        weaviate_url: Optional[str] = None,
        weaviate_api_key: Optional[str] = None,
        index_name: str = "EssenceAI"
    ):
        """Initialize Weaviate RAG engine."""
        super().__init__(data_dir, persist_dir, cache_dir)
        
        # Weaviate configuration
        self.weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL")
        self.weaviate_api_key = weaviate_api_key or os.getenv("WEAVIATE_API_KEY")
        self.index_name = index_name
        self.vector_store = None
        
        self._setup_embeddings()
        self._setup_base_llm(model="gpt-4o-mini", temperature=0.1)
        self._setup_base_node_parser(chunk_size=300, chunk_overlap=30)

    def _setup_embeddings(self):
        """Configure embeddings for Weaviate."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Use standard OpenAI embedding with small batches
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=api_key,
            embed_batch_size=3  # Very small to avoid rate limits
        )

        logger.info("✓ Using OpenAI embeddings (batch size: 3)")

    def _setup_weaviate(self):
        """Set up Weaviate vector store."""
        try:
            import weaviate
            from weaviate.classes.init import Auth
        except ImportError:
            raise ImportError(
                "Weaviate client not installed. Run: pip install weaviate-client"
            )

        if not self.weaviate_url:
            raise ValueError(
                "WEAVIATE_URL not set. Get a free cluster at https://console.weaviate.cloud"
            )

        logger.info(f"🔗 Connecting to Weaviate at {self.weaviate_url}")

        # Connect to Weaviate Cloud (v4 API)
        if self.weaviate_api_key:
            client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.weaviate_url,
                auth_credentials=Auth.api_key(self.weaviate_api_key),
                headers={
                    "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
                }
            )
        else:
            client = weaviate.connect_to_custom(
                http_host=self.weaviate_url.replace("https://", "").replace("http://", ""),
                http_secure=self.weaviate_url.startswith("https"),
                headers={
                    "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
                }
            )

        # Create vector store
        self.vector_store = WeaviateVectorStore(
            weaviate_client=client,
            index_name=self.index_name
        )

        logger.info(f"✓ Connected to Weaviate (index: {self.index_name})")
        return client

    def initialize_index(self, force_reload: bool = False) -> bool:
        """
        Load or create index using Weaviate.
        Embeddings are stored in Weaviate Cloud!
        
        Args:
            force_reload: Force rebuilding the index
            
        Returns:
            True if successful
        """
        try:
            # Set up Weaviate
            weaviate_client = self._setup_weaviate()

            # Check if index already exists in Weaviate (v4 API)
            try:
                collection = weaviate_client.collections.get(self.index_name)
                index_exists = True
                logger.info(f"📚 Found existing collection: {self.index_name}")
            except Exception:
                index_exists = False
                logger.info(f"📝 Collection {self.index_name} does not exist yet")

            if index_exists and not force_reload:
                logger.info("📚 Loading existing index from Weaviate...")

                # Load from Weaviate
                storage_context = StorageContext.from_defaults(
                    vector_store=self.vector_store
                )
                self.index = VectorStoreIndex.from_vector_store(
                    self.vector_store,
                    storage_context=storage_context
                )

                logger.info("✓ Index loaded from Weaviate (no embedding cost!)")

            else:
                if force_reload and index_exists:
                    logger.info("🗑️ Deleting existing index...")
                    weaviate_client.collections.delete(self.index_name)

                logger.info(f"📄 Building new index from {self.data_dir}...")

                if not self.data_dir.exists():
                    raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

                # Load documents
                documents = SimpleDirectoryReader(
                    str(self.data_dir),
                    required_exts=[".pdf"]
                ).load_data()

                if not documents:
                    raise ValueError(f"No PDF files found in {self.data_dir}")

                logger.info(f"✓ Loaded {len(documents)} documents")
                logger.info("⚙️ Creating embeddings and uploading to Weaviate...")
                logger.info("   (This is a one-time cost - embeddings will be stored in Weaviate)")

                # Create storage context with Weaviate
                storage_context = StorageContext.from_defaults(
                    vector_store=self.vector_store
                )

                # Create index - embeddings will be stored in Weaviate
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    storage_context=storage_context,
                    show_progress=True
                )

                logger.info("✓ Index created and stored in Weaviate!")

            # Create query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=2,
                response_mode="compact"
            )

            return True

        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            raise
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except FileNotFoundError as e:
            logger.error(f"Data directory or files not found: {e}")
            raise
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Weaviate connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing Weaviate index: {e}", exc_info=True)
            raise
