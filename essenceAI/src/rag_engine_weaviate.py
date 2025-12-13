"""
Weaviate-based RAG Engine
Uses Weaviate Cloud as vector store - embeddings are stored remotely
This eliminates the need to rebuild embeddings every time!
"""

import os
import hashlib
import time
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dotenv import load_dotenv
import json
import logging

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
    Document
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.weaviate import WeaviateVectorStore

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeaviateRAGEngine:
    """
    RAG engine using Weaviate Cloud for vector storage.
    Embeddings are stored in Weaviate, so you only pay once!
    """

    def __init__(
        self,
        data_dir: str = "data",
        cache_dir: str = ".cache",
        weaviate_url: Optional[str] = None,
        weaviate_api_key: Optional[str] = None,
        index_name: str = "EssenceAI"
    ):
        self.data_dir = Path(data_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Weaviate configuration
        self.weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL")
        self.weaviate_api_key = weaviate_api_key or os.getenv("WEAVIATE_API_KEY")
        self.index_name = index_name

        self.index = None
        self.query_engine = None
        self.vector_store = None

        # Query cache to avoid repeated API calls
        self.query_cache = {}
        self._load_query_cache()

        self._setup_llm()

    def _setup_llm(self):
        """Configure LLM with standard embeddings."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")

        # Use standard OpenAI embedding with small batches
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=api_key,
            embed_batch_size=3  # Very small to avoid rate limits
        )

        logger.info("✓ Using OpenAI embeddings (batch size: 3)")

        # Use GPT-4o-mini for queries
        Settings.llm = OpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0.1
        )

        # Smaller chunks
        Settings.node_parser = SentenceSplitter(
            chunk_size=300,
            chunk_overlap=30
        )

    def _load_query_cache(self):
        """Load cached queries from disk."""
        cache_file = self.cache_dir / "query_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.query_cache = json.load(f)
                logger.info(f"📦 Loaded {len(self.query_cache)} cached queries")
            except:
                self.query_cache = {}

    def _save_query_cache(self):
        """Save query cache to disk."""
        cache_file = self.cache_dir / "query_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(self.query_cache, f)

    def _get_query_hash(self, query: str) -> str:
        """Generate hash for query caching."""
        return hashlib.md5(query.encode()).hexdigest()

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
                print("\n" + "="*70)
                print("📥 Step 1/4: Loading PDF documents")
                print("="*70)
                print(f"   Reading from: {self.data_dir}")
                documents = SimpleDirectoryReader(
                    str(self.data_dir),
                    required_exts=[".pdf"]
                ).load_data()

                if not documents:
                    raise ValueError(f"No PDF files found in {self.data_dir}")

                print(f"✓ Loaded {len(documents)} PDF documents")
                total_chars = sum(len(doc.text) for doc in documents)
                print(f"   Total content: {total_chars:,} characters")
                print()

                print("="*70)
                print("🔄 Step 2/4: Parsing documents into chunks")
                print("="*70)
                print(f"   Chunk size: 300 tokens")
                print(f"   Overlap: 30 tokens")
                print(f"   This creates searchable text segments...")
                print()

                print("="*70)
                print("🤖 Step 3/4: Generating embeddings (OpenAI API)")
                print("="*70)
                print("   ⚠️  This step takes 5-10 minutes due to rate limits")
                print("   📊 Processing in batches of 3...")
                print("   💰 Cost: ~$0.003 (one-time, stored in Weaviate)")
                print("   ⏱️  Started at:", time.strftime("%H:%M:%S"))
                print()

                # Create storage context with Weaviate
                storage_context = StorageContext.from_defaults(
                    vector_store=self.vector_store
                )

                # Create index - embeddings will be stored in Weaviate
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    storage_context=storage_context,
                    show_progress=True  # Shows progress bar
                )

                print()
                print("="*70)
                print("☁️  Step 4/4: Uploading to Weaviate Cloud")
                print("="*70)
                print(f"   Cluster: {self.weaviate_url[:50]}...")
                print(f"✓ Index created and stored in Weaviate!")
                print(f"✓ Embeddings saved to cloud (index: {self.index_name})")
                print(f"   Finished at: {time.strftime('%H:%M:%S')}")
                print()
                print("💡 Next time: Index loads in <1 second from Weaviate!")
                print("="*70)
                print()

            # Create query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=2,
                response_mode="compact"
            )

            return True

        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            raise

    def get_cited_answer(self, query: str, use_cache: bool = True) -> Tuple[str, List[Dict]]:
        """
        Query with caching to avoid repeated API calls.
        """
        if not self.query_engine:
            raise RuntimeError("Index not initialized")

        # Check cache first
        query_hash = self._get_query_hash(query)
        if use_cache and query_hash in self.query_cache:
            logger.info("💾 Using cached result (no API call)")
            cached = self.query_cache[query_hash]
            return cached['answer'], cached['citations']

        try:
            # Make API call
            response = self.query_engine.query(query)
            answer = str(response)

            # Extract citations
            citations = []
            if hasattr(response, 'source_nodes'):
                for i, node in enumerate(response.source_nodes):
                    metadata = node.node.metadata if hasattr(node.node, 'metadata') else {}
                    file_name = Path(metadata.get('file_name', 'Unknown')).stem
                    page_num = metadata.get('page_label', 'N/A')
                    score = round(node.score, 3) if hasattr(node, 'score') else None
                    text_excerpt = node.node.text[:200] + "..."

                    citations.append({
                        "source_id": i + 1,
                        "file_name": file_name,
                        "page": page_num,
                        "relevance_score": score,
                        "excerpt": text_excerpt
                    })

            # Cache the result
            self.query_cache[query_hash] = {
                'answer': answer,
                'citations': citations
            }
            self._save_query_cache()

            return answer, citations

        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            raise

    def query(self, query_str: str):
        """
        Query method for compatibility with different interfaces.
        Returns the query engine's response object.
        """
        if not self.query_engine:
            raise RuntimeError("Index not initialized")
        return self.query_engine.query(query_str)

    def get_citations(self, response) -> List[Dict]:
        """
        Extract citations from a response object.
        """
        citations = []
        if hasattr(response, 'source_nodes'):
            for i, node in enumerate(response.source_nodes):
                metadata = node.node.metadata if hasattr(node.node, 'metadata') else {}
                file_name = Path(metadata.get('file_name', 'Unknown')).stem
                citations.append({
                    "source_id": i + 1,
                    "file_name": file_name,
                    "page": metadata.get('page_label', 'N/A'),
                    "relevance_score": round(node.score, 3) if hasattr(node, 'score') else None,
                    "excerpt": node.node.text[:200] + "..." if len(node.node.text) > 200 else node.node.text
                })
        return citations

    def get_marketing_strategy(
        self,
        product_concept: str,
        category: str,
        target_segment: str = "Skeptic"
    ) -> Tuple[str, List[Dict]]:
        """Get marketing strategy with caching."""
        query = f"""Based on research about {category} and {target_segment} consumers:

Product: {product_concept}

Provide a concise marketing strategy (3-4 key points) addressing:
1. Key psychological factors for this segment
2. Recommended messaging approach
3. What to avoid

Cite specific research findings."""

        return self.get_cited_answer(query)

    def get_consumer_insights(self, category: str) -> Tuple[str, List[Dict]]:
        """Get consumer insights with caching."""
        query = f"""Summarize key consumer acceptance factors for {category} products:
- Main barriers
- Success factors
- Role of familiarity"""

        return self.get_cited_answer(query)

    def clear_cache(self):
        """Clear query cache to force fresh API calls."""
        self.query_cache = {}
        self._save_query_cache()
        logger.info("🗑️ Cache cleared")

    def close(self):
        """Close Weaviate connection properly."""
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
                logger.info("✓ Weaviate connection closed")
            except Exception as e:
                logger.warning(f"Error closing Weaviate connection: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.close()
        return False

    def __del__(self):
        """Destructor - cleanup when object is garbage collected."""
        self.close()
