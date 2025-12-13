"""
RAG (Retrieval-Augmented Generation) Engine
Uses LlamaIndex to read research PDFs and provide cited answers.
This is the "Brain" of essenceAI - it ensures Scientific Quality by citing sources.
"""

import os
import time
from typing import List, Dict, Tuple
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.openai import OpenAIEmbedding

# Load environment variables
load_dotenv()


class RAGEngine:
    """
    Manages the RAG pipeline for scientific paper analysis.
    Provides cited answers from research PDFs.
    """

    def __init__(self, data_dir: str = "data", persist_dir: str = ".storage"):
        """
        Initialize the RAG engine.

        Args:
            data_dir: Directory containing PDF files
            persist_dir: Directory to store the index
        """
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        self.index = None
        self.query_engine = None

        # Configure LLM and embeddings with rate limiting
        self._setup_llm()
        self._setup_embeddings()

    def _setup_embeddings(self):
        """Configure embeddings with smaller batch sizes to avoid rate limits."""
        # Use very small embed batch size to avoid rate limits
        # With 40K TPM limit and ~500 tokens per chunk, we can do about 3-4 chunks per batch
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-ada-002",
            embed_batch_size=3,  # Very small to stay under 40K token limit
        )

        # Set smaller chunk size to reduce tokens per request
        Settings.chunk_size = 400  # Small chunks to stay under rate limits
        Settings.chunk_overlap = 40

    def _setup_llm(self):
        """Configure the LLM provider (OpenAI or Anthropic)."""
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

        if llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            Settings.llm = Anthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=api_key,
                temperature=0.1
            )
        else:  # default to openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            Settings.llm = OpenAI(
                model="gpt-4o",
                api_key=api_key,
                temperature=0.1
            )


    def initialize_index(self, force_reload: bool = False) -> bool:
        """
        Load or create the vector index from PDFs.

        Args:
            force_reload: If True, rebuild index even if it exists

        Returns:
            True if successful
        """
        try:
            # Check if we can load existing index
            if not force_reload and self.persist_dir.exists():
                print("📚 Loading existing index...")
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(self.persist_dir)
                )
                self.index = load_index_from_storage(storage_context)
                print("✓ Index loaded successfully")
            else:
                # Build new index from PDFs
                print(f"📄 Building index from PDFs in {self.data_dir}...")

                if not self.data_dir.exists():
                    raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

                # Load documents
                print("📥 Loading documents (this may take a while due to rate limits)...")
                documents = SimpleDirectoryReader(
                    str(self.data_dir),
                    required_exts=[".pdf"]
                ).load_data()

                if not documents:
                    raise ValueError(f"No PDF files found in {self.data_dir}")

                print(f"✓ Loaded {len(documents)} documents")
                print("⏳ Creating embeddings (processing in small batches to avoid rate limits)...")
                print("   This will take several minutes. Please be patient...")

                # Process documents in small batches to avoid rate limits
                # Create index from first batch
                batch_size = 5  # Process 5 documents at a time
                batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]

                print(f"   Processing {len(batches)} batches...")

                # Create initial index with first batch
                self.index = VectorStoreIndex.from_documents(
                    batches[0],
                    show_progress=True
                )
                print(f"   ✓ Batch 1/{len(batches)} complete")

                # Add remaining batches with delays
                for i, batch in enumerate(batches[1:], start=2):
                    time.sleep(2)  # 2 second delay between batches
                    for doc in batch:
                        self.index.insert(doc)
                    print(f"   ✓ Batch {i}/{len(batches)} complete")

                # Persist index
                self.persist_dir.mkdir(exist_ok=True)
                self.index.storage_context.persist(persist_dir=str(self.persist_dir))
                print(f"✓ Index created and saved to {self.persist_dir}")

            # Create query engine with citation support
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=3,
                response_mode="compact"
            )

            return True

        except Exception as e:
            print(f"✗ Error initializing index: {str(e)}")
            raise

    def get_cited_answer(self, query: str) -> Tuple[str, List[Dict]]:
        """
        Query the index and return answer with citations.

        Args:
            query: The question to ask

        Returns:
            Tuple of (answer_text, list_of_source_citations)
        """
        if not self.query_engine:
            raise RuntimeError("Index not initialized. Call initialize_index() first.")

        try:
            # Query the engine
            response = self.query_engine.query(query)

            # Extract answer
            answer = str(response)

            # Extract source citations
            citations = []
            if hasattr(response, 'source_nodes'):
                for i, node in enumerate(response.source_nodes):
                    # Get metadata
                    metadata = node.node.metadata if hasattr(node.node, 'metadata') else {}

                    # Extract filename
                    file_name = metadata.get('file_name', 'Unknown')
                    if file_name != 'Unknown':
                        # Clean up filename
                        file_name = Path(file_name).stem

                    # Get page number if available
                    page_num = metadata.get('page_label', metadata.get('page_number', 'N/A'))

                    # Get relevance score
                    score = round(node.score, 3) if hasattr(node, 'score') else None

                    # Get text excerpt
                    text_excerpt = node.node.text[:300] + "..." if len(node.node.text) > 300 else node.node.text

                    citation = {
                        "source_id": i + 1,
                        "file_name": file_name,
                        "page": page_num,
                        "relevance_score": score,
                        "excerpt": text_excerpt
                    }

                    citations.append(citation)

            return answer, citations

        except Exception as e:
            print(f"✗ Error querying index: {str(e)}")
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

    def get_marketing_strategy(
        self,
        product_concept: str,
        category: str,
        target_segment: str = "Skeptic"
    ) -> Tuple[str, List[Dict]]:
        """
        Get a marketing strategy based on research papers.

        Args:
            product_concept: Description of the product
            category: One of "Precision Fermentation", "Plant-Based", "Algae"
            target_segment: "High Essentialist", "Skeptic", or "Non-Consumer"

        Returns:
            Tuple of (strategy_text, citations)
        """
        query = f"""Based on the research papers about food essentialism and consumer acceptance:

Product Concept: {product_concept}
Category: {category}
Target Consumer Segment: {target_segment}

Provide a specific marketing strategy that addresses:
1. What psychological factors influence this segment's acceptance?
2. What messaging should be emphasized (e.g., sensory mimicry vs. naturalness)?
3. What should be avoided in marketing to this segment?
4. How does processing perception affect this segment?

Cite specific findings from the research papers."""

        return self.get_cited_answer(query)

    def get_general_strategy(
        self,
        product_concept: str,
        category: str
    ) -> Tuple[str, List[Dict]]:
        """
        Get a general marketing strategy without segment-specific targeting.

        Args:
            product_concept: Description of the product
            category: One of "Precision Fermentation", "Plant-Based", "Algae"

        Returns:
            Tuple of (strategy_text, citations)
        """
        query = f"""Based on the research papers about consumer acceptance of sustainable food alternatives:

Product Concept: {product_concept}
Category: {category}

Provide a comprehensive marketing strategy that addresses:
1. What are the main factors influencing consumer acceptance in this category?
2. What messaging approaches are most effective based on research?
3. What are the key barriers to overcome?
4. How can the product be positioned to maximize acceptance across different consumer types?
5. What role does familiarity and habituation play?

Cite specific findings from the research papers."""

        return self.get_cited_answer(query)

    def get_segment_strategy(
        self,
        product_concept: str,
        target_segment: str
    ) -> Tuple[str, List[Dict]]:
        """
        Get a segment-specific strategy without category restriction.

        Args:
            product_concept: Description of the product
            target_segment: "High Essentialist", "Skeptic", or "Non-Consumer"

        Returns:
            Tuple of (strategy_text, citations)
        """
        query = f"""Based on the research papers about food essentialism and consumer acceptance:

Product Concept: {product_concept}
Target Consumer Segment: {target_segment}
Domain: All sustainable food alternatives (Precision Fermentation, Plant-Based, Algae)

Provide a specific marketing strategy that addresses:
1. What psychological factors influence this segment's acceptance across all sustainable food categories?
2. What messaging should be emphasized for this segment regardless of product type?
3. What should be avoided in marketing to this segment?
4. How does processing perception affect this segment's acceptance?

Cite specific findings from the research papers."""

        return self.get_cited_answer(query)

    def get_universal_strategy(
        self,
        product_concept: str
    ) -> Tuple[str, List[Dict]]:
        """
        Get a universal marketing strategy without category or segment restrictions.

        Args:
            product_concept: Description of the product

        Returns:
            Tuple of (strategy_text, citations)
        """
        query = f"""Based on the research papers about consumer acceptance of sustainable food alternatives:

Product Concept: {product_concept}

Provide a comprehensive, universal marketing strategy that addresses:
1. What are the main factors influencing consumer acceptance across all sustainable food categories?
2. What messaging approaches work best across different consumer segments?
3. What are the universal barriers to overcome?
4. How can the product be positioned to maximize broad market acceptance?
5. What role do familiarity, processing perception, and labeling play?

Cite specific findings from the research papers."""

        return self.get_cited_answer(query)

    def get_consumer_insights(self, category: str) -> Tuple[str, List[Dict]]:
        """
        Get general consumer insights for a category.

        Args:
            category: Product category

        Returns:
            Tuple of (insights_text, citations)
        """
        query = f"""What are the key consumer acceptance factors for {category} products according to the research papers?

Include:
- Main barriers to acceptance
- Factors that increase acceptance
- Role of familiarity and habituation
- Impact of labeling (open vs closed label)"""

        return self.get_cited_answer(query)

    def verify_claim(self, claim: str) -> Tuple[str, List[Dict]]:
        """
        Verify a marketing claim against research papers.

        Args:
            claim: The claim to verify

        Returns:
            Tuple of (verification_result, citations)
        """
        query = f"""Verify this claim against the research papers: "{claim}"

Is this claim supported by the research? What evidence exists for or against it?"""

        return self.get_cited_answer(query)
