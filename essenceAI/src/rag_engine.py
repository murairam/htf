"""
RAG (Retrieval-Augmented Generation) Engine
Uses LlamaIndex to read research PDFs and provide cited answers.
This is the "Brain" of essenceAI - it ensures Scientific Quality by citing sources.
"""

import os
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
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

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

        # Configure LLM based on environment variable
        self._setup_llm()

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
                documents = SimpleDirectoryReader(
                    str(self.data_dir),
                    required_exts=[".pdf"]
                ).load_data()

                if not documents:
                    raise ValueError(f"No PDF files found in {self.data_dir}")

                print(f"✓ Loaded {len(documents)} documents")

                # Create index
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    show_progress=True
                )

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
