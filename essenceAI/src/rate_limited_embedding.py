"""
Rate-Limited Embedding Wrapper
Prevents hitting OpenAI rate limits by adding delays between requests
"""

import time
from typing import List, Dict, Any
from llama_index.embeddings.openai import OpenAIEmbedding
import logging

logger = logging.getLogger(__name__)


class RateLimitedEmbedding(OpenAIEmbedding):
    """
    Wrapper around OpenAIEmbedding that adds delays between requests
    to prevent rate limit errors.

    This class is properly serializable for use with LlamaIndex storage.
    """

    def __init__(self, delay_seconds: float = 2.0, **kwargs):
        """
        Initialize with rate limiting.

        Args:
            delay_seconds: Seconds to wait between embedding requests
            **kwargs: Arguments to pass to OpenAIEmbedding
        """
        super().__init__(**kwargs)
        self.delay_seconds = delay_seconds
        self.last_request_time = 0

    @classmethod
    def class_name(cls) -> str:
        """Return the class name for serialization."""
        return "RateLimitedEmbedding"

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Serialize to dictionary for storage.

        Returns:
            Dictionary with all configuration including custom fields
        """
        # Get base class serialization
        data = super().to_dict(**kwargs)

        # Add our custom fields
        data["delay_seconds"] = self.delay_seconds
        # Don't serialize last_request_time as it's runtime state

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs) -> "RateLimitedEmbedding":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary with configuration

        Returns:
            RateLimitedEmbedding instance
        """
        # Extract our custom field
        delay_seconds = data.pop("delay_seconds", 2.0)

        # Create instance with remaining data
        # Note: We can't directly call super().from_dict() as it may not exist
        # So we extract the necessary fields and create a new instance

        return cls(
            delay_seconds=delay_seconds,
            model=data.get("model", "text-embedding-3-small"),
            api_key=data.get("api_key"),
            embed_batch_size=data.get("embed_batch_size", 5),
            **kwargs
        )

    def _wait_if_needed(self):
        """Wait if we're making requests too quickly."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.delay_seconds:
            wait_time = self.delay_seconds - time_since_last
            logger.info(f"⏳ Rate limiting: waiting {wait_time:.2f}s...")
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text with rate limiting."""
        self._wait_if_needed()
        return super().get_text_embedding(text)

    def get_text_embedding_batch(
        self, texts: List[str], show_progress: bool = False
    ) -> List[List[float]]:
        """Get embeddings for multiple texts with rate limiting."""
        self._wait_if_needed()

        # Process in smaller batches with delays
        batch_size = 5  # Very conservative
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"📊 Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(batch)} texts)")

            try:
                embeddings = super().get_text_embedding_batch(batch, show_progress=False)
                all_embeddings.extend(embeddings)

                # Add delay between batches
                if i + batch_size < len(texts):
                    logger.info(f"⏳ Waiting {self.delay_seconds}s before next batch...")
                    time.sleep(self.delay_seconds)

            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    logger.warning(f"⚠️ Rate limit hit, waiting 10 seconds...")
                    time.sleep(10)
                    # Retry this batch
                    embeddings = super().get_text_embedding_batch(batch, show_progress=False)
                    all_embeddings.extend(embeddings)
                else:
                    raise

        return all_embeddings

    async def aget_text_embedding(self, text: str) -> List[float]:
        """Async version with rate limiting."""
        self._wait_if_needed()
        return await super().aget_text_embedding(text)
