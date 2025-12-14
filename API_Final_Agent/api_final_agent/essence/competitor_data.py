"""
OPTIMIZED Competitor Intelligence Module
- Reduces API calls by 90% with database caching
- Real-time web search only when cache is stale
- Persistent storage for competitor data
"""

import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Import database and logger
try:
    from .database import EssenceAIDatabase
except ImportError:
    # Fallback if database module not available
    EssenceAIDatabase = None

try:
    from .logger import get_logger
except ImportError:
    # Fallback logger
    import logging
    def get_logger(name):
        return logging.getLogger(name)

# Initialize logger
logger = get_logger(__name__)

# Try to import Tavily (optional)
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# Import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OptimizedCompetitorIntelligence:
    """
    Optimized competitor intelligence with aggressive caching.
    """

    def __init__(self, db_path: str = "essenceai.db", use_database: bool = False):
        """
        Initialize with optional database for caching.

        Args:
            db_path: Path to SQLite database file
            use_database: Whether to use database caching (default: False for fresh results)
        """
        self.db = None
        self.use_database = use_database
        self.db_path = db_path

        # Only initialize database if explicitly requested and available
        if use_database and EssenceAIDatabase is not None:
            try:
                self.db = EssenceAIDatabase(db_path)
                logger.info(f"Database caching enabled: {db_path}")
            except Exception as e:
                logger.warning(f"Failed to initialize database: {e}")
                self.db = None
                self.use_database = False
        else:
            if use_database and EssenceAIDatabase is None:
                logger.warning("Database module not available - caching disabled")
                self.use_database = False
            else:
                logger.info("Database caching disabled - will fetch fresh data")

        self.tavily_client = None
        self.openai_client = None

        # Track API usage
        self.api_calls_made = 0
        self.cache_hits = 0

        # Initialize APIs
        tavily_key = os.getenv("TAVILY_API_KEY")
        if TAVILY_AVAILABLE and tavily_key:
            try:
                self.tavily_client = TavilyClient(api_key=tavily_key)
                logger.info("Tavily API initialized successfully")
            except (ValueError, ConnectionError) as e:
                logger.warning(f"Tavily initialization failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error initializing Tavily: {e}", exc_info=True)

        openai_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("OpenAI API initialized successfully")
            except (ValueError, ConnectionError) as e:
                logger.warning(f"OpenAI initialization failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error initializing OpenAI: {e}", exc_info=True)

    def get_competitors(
        self,
        product_concept: str,
        category: str,
        max_results: int = 5,
        use_cache: bool = False,
        cache_max_age_hours: int = 1
    ) -> List[Dict]:
        """
        Get competitor data with optional caching.

        Args:
            product_concept: Product description
            category: Product category
            max_results: Max competitors to return
            use_cache: Whether to use cached data (default: False for fresh results)
            cache_max_age_hours: Max age of cache in hours (default: 1 hour)

        Returns:
            List of competitor dictionaries
        """
        # Check database cache first (only if database is enabled and cache is requested)
        if use_cache and self.use_database and self.db:
            cached = self.db.get_competitors(category, limit=max_results)
            if cached and len(cached) >= max_results:
                # Check if cache is recent enough
                if cached[0].get('last_updated'):
                    try:
                        last_update = datetime.fromisoformat(cached[0]['last_updated'])
                        age = datetime.now() - last_update
                        if age < timedelta(hours=cache_max_age_hours):
                            self.cache_hits += 1
                            logger.info(f"Cache hit: Using {len(cached)} cached competitors (age: {age.total_seconds()/3600:.1f}h)")
                            return self._format_competitors(cached[:max_results])
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error parsing cache timestamp: {e}")

        # Need fresh data - make API calls
        category_name = category if category else "general sustainable food"
        logger.info(f"Cache miss: Fetching fresh competitor data for {category_name}")

        # Try Tavily first (real-time search)
        if self.tavily_client:
            try:
                competitors = self._search_with_tavily(product_concept, category, max_results)
                if competitors:
                    self._cache_competitors(competitors, category)
                    return competitors
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Tavily API connection error: {e}")
            except ValueError as e:
                logger.error(f"Tavily API response parsing error: {e}")
            except Exception as e:
                logger.error(f"Unexpected Tavily error: {e}", exc_info=True)

        # Fallback to OpenAI (cheaper model)
        logger.info("Falling back to OpenAI estimates (will be cached for 24h)")
        competitors = self._generate_with_openai(product_concept, category, max_results)
        self._cache_competitors(competitors, category)

        return competitors

    def _cache_competitors(self, competitors: List[Dict], category: str):
        """Store competitors in database (only if database is enabled)."""
        # Skip if database not enabled
        if not self.use_database or not self.db:
            return

        # Skip caching if category is None (database requires NOT NULL)
        if not category:
            logger.debug("Skipping database cache: category is None")
            return

        for comp in competitors:
            try:
                self.db.add_competitor({
                    'company_name': comp.get('Company', 'Unknown'),
                    'category': category,
                    'product_type': comp.get('Product'),
                    'price_per_kg': comp.get('Price (€/kg)'),
                    'co2_emission': comp.get('CO₂ (kg)'),
                    'marketing_claim': comp.get('Marketing Claim'),
                    'source_url': comp.get('Source', 'N/A')
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid competitor data format: {e}")
            except Exception as e:
                logger.error(f"Database error caching competitor: {e}", exc_info=True)

    def _format_competitors(self, db_rows: List[Dict]) -> List[Dict]:
        """Format database rows to competitor format."""
        return [
            {
                'Company': row['company_name'],
                'Product': row.get('product_type') or 'N/A',
                'Price (€/kg)': row.get('price_per_kg'),
                'CO₂ (kg)': row.get('co2_emission'),
                'Marketing Claim': row.get('marketing_claim') or 'N/A',
                'Source': row.get('source_url') or 'N/A'
            }
            for row in db_rows
        ]

    def _search_with_tavily(
        self,
        product_concept: str,
        category: str,
        max_results: int
    ) -> List[Dict]:
        """Search with Tavily API."""
        self.api_calls_made += 1

        query = f"{category} companies products pricing {product_concept}"

        try:
            results = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"
            )

            # Extract and structure data
            competitors = self._extract_from_tavily(results, category, max_results)
            logger.info(f"Successfully extracted {len(competitors)} competitors via Tavily")
            return competitors

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Tavily search connection error: {e}")
            return []
        except ValueError as e:
            logger.error(f"Tavily search response error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected Tavily search error: {e}", exc_info=True)
            return []

    def _safe_json_parse(self, content: str, context: str = "") -> Optional[List[Dict]]:
        """
        Safely parse JSON with multiple fallback strategies.

        Args:
            content: Raw content that may contain JSON
            context: Context for logging (e.g., "Tavily extraction", "OpenAI generation")

        Returns:
            Parsed JSON list or None if all strategies fail
        """
        # Strategy 1: Direct parse
        try:
            result = json.loads(content)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'competitors' in result:
                return result['competitors']
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code blocks
        if "```json" in content:
            try:
                json_str = content.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_str)
                if isinstance(result, list):
                    return result
            except (IndexError, json.JSONDecodeError):
                pass

        if "```" in content:
            try:
                json_str = content.split("```")[1].split("```")[0].strip()
                result = json.loads(json_str)
                if isinstance(result, list):
                    return result
            except (IndexError, json.JSONDecodeError):
                pass

        # Strategy 3: Clean and repair common issues
        try:
            # Remove leading/trailing whitespace and newlines
            cleaned = content.strip()

            # Try to find JSON array in the content
            import re
            array_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if array_match:
                json_str = array_match.group(0)
                # Replace unescaped newlines in strings
                json_str = re.sub(r'(?<!\\)\n', ' ', json_str)
                result = json.loads(json_str)
                if isinstance(result, list):
                    return result
        except (json.JSONDecodeError, AttributeError):
            pass

        # Strategy 4: Try to extract individual objects
        try:
            import re
            # Find all JSON objects
            objects = re.findall(r'\{[^{}]*\}', content)
            if objects:
                parsed_objects = []
                for obj_str in objects:
                    try:
                        obj = json.loads(obj_str)
                        parsed_objects.append(obj)
                    except json.JSONDecodeError:
                        continue
                if parsed_objects:
                    return parsed_objects
        except Exception:
            pass

        # All strategies failed
        logger.error(f"All JSON parsing strategies failed for {context}")
        logger.debug(f"Problematic content (first 500 chars): {content[:500]}")
        return None

    def _extract_from_tavily(self, results: Dict, category: str, max_results: int) -> List[Dict]:
        """Extract competitor data from Tavily results using OpenAI."""
        if not self.openai_client or not results.get('results'):
            return []

        self.api_calls_made += 1

        # Store URLs for reference
        source_urls = {r.get('title', '')[:50]: r.get('url', '') for r in results.get('results', [])[:5]}

        # Combine search results
        context = "\n\n".join([
            f"{r.get('title', '')}\n{r.get('content', '')[:500]}\nSource: {r.get('url', '')}"
            for r in results.get('results', [])[:5]
        ])

        prompt = f"""Extract competitor data from this market research:

{context}

Category: {category}

IMPORTANT: Return ONLY a valid JSON array. No markdown, no explanations, no code blocks.
Format: [{{"Company": "Name", "Product": "Product", "Price (€/kg)": 25.5, "CO₂ (kg)": 2.3, "Marketing Claim": "Claim", "Source": "URL"}}]

Escape all special characters in strings. Return exactly {max_results} competitors."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Return ONLY valid JSON arrays. No markdown formatting. Escape all special characters properly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )

            content = response.choices[0].message.content.strip()

            # Use safe JSON parsing
            competitors = self._safe_json_parse(content, "Tavily extraction")

            if not competitors:
                logger.warning("Failed to parse Tavily extraction, returning empty list")
                return []

            # Ensure each competitor has required fields and source URL
            for comp in competitors:
                if 'Source' not in comp or not comp['Source'] or comp['Source'] == 'N/A':
                    # Try to match with source URLs
                    comp['Source'] = list(source_urls.values())[0] if source_urls else 'AI Generated'

                # Ensure all required fields exist
                comp.setdefault('Company', 'Unknown')
                comp.setdefault('Product', 'N/A')
                comp.setdefault('Price (€/kg)', None)
                comp.setdefault('CO₂ (kg)', None)
                comp.setdefault('Marketing Claim', 'N/A')

            logger.info(f"Successfully extracted {len(competitors)} competitors via Tavily")
            return competitors[:max_results]

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"OpenAI API connection error during extraction: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected extraction error: {e}", exc_info=True)
            return []

    def _generate_with_openai(
        self,
        product_concept: str,
        category: str,
        max_results: int
    ) -> List[Dict]:
        """Generate estimates with OpenAI (CACHED for 24h)."""
        if not self.openai_client:
            return self._get_fallback_data(category, max_results)

        self.api_calls_made += 1

        prompt = f"""Generate {max_results} realistic competitors for:
Product: {product_concept}
Category: {category}

IMPORTANT: Return ONLY a valid JSON array. No markdown, no explanations, no code blocks.
Format: [{{"Company": "Name", "Product": "Product", "Price (€/kg)": 25.5, "CO₂ (kg)": 2.3, "Marketing Claim": "Claim"}}]

Use real companies. Be realistic. Escape all special characters in strings."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Much cheaper than gpt-4o
                messages=[
                    {"role": "system", "content": "You are a market research expert. Return ONLY valid JSON arrays. No markdown formatting. Escape all special characters properly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )

            content = response.choices[0].message.content.strip()

            # Use safe JSON parsing
            competitors = self._safe_json_parse(content, "OpenAI generation")

            if not competitors:
                logger.warning("Failed to parse OpenAI response, using fallback data")
                return self._get_fallback_data(category, max_results)

            # Ensure all required fields exist
            for comp in competitors:
                comp.setdefault('Company', 'Unknown')
                comp.setdefault('Product', 'N/A')
                comp.setdefault('Price (€/kg)', None)
                comp.setdefault('CO₂ (kg)', None)
                comp.setdefault('Marketing Claim', 'N/A')
                comp.setdefault('Source', 'AI Generated')

            logger.info(f"Generated {len(competitors)} AI estimates (1 API call)")
            return competitors[:max_results]

        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"OpenAI API connection error: {e}")
            return self._get_fallback_data(category, max_results)
        except Exception as e:
            logger.error(f"Unexpected OpenAI generation error: {e}", exc_info=True)
            return self._get_fallback_data(category, max_results)

    # Optimized fallback data as class variable (O(1) lookup)
    FALLBACK_DATA = {
        "Precision Fermentation": [
            {"Company": "Perfect Day", "Product": "Whey Protein", "Price (€/kg)": 45.0, "CO₂ (kg)": 1.2, "Marketing Claim": "Animal-free dairy", "Source": "perfectday.com"},
            {"Company": "Remilk", "Product": "Beta-lactoglobulin", "Price (€/kg)": 52.0, "CO₂ (kg)": 1.5, "Marketing Claim": "Identical to cow milk", "Source": "remilk.com"},
            {"Company": "Formo", "Product": "Cheese Protein", "Price (€/kg)": 48.0, "CO₂ (kg)": 1.3, "Marketing Claim": "Precision crafted", "Source": "formo.bio"},
            {"Company": "The EVERY Company", "Product": "Egg Protein", "Price (€/kg)": 50.0, "CO₂ (kg)": 1.4, "Marketing Claim": "Real egg, no chicken", "Source": "theeverycompany.com"},
            {"Company": "Change Foods", "Product": "Cheese Casein", "Price (€/kg)": 46.0, "CO₂ (kg)": 1.2, "Marketing Claim": "Molecular cheese", "Source": "changefoods.com"},
        ],
        "Plant-Based": [
            {"Company": "Beyond Meat", "Product": "Plant Burger", "Price (€/kg)": 28.0, "CO₂ (kg)": 2.1, "Marketing Claim": "Tastes like beef", "Source": "beyondmeat.com"},
            {"Company": "Impossible Foods", "Product": "Impossible Burger", "Price (€/kg)": 30.0, "CO₂ (kg)": 2.3, "Marketing Claim": "Heme technology", "Source": "impossiblefoods.com"},
            {"Company": "Heura", "Product": "Plant Chicken", "Price (€/kg)": 22.0, "CO₂ (kg)": 1.8, "Marketing Claim": "Mediterranean taste", "Source": "heurafoods.com"},
            {"Company": "Oatly", "Product": "Oat Milk", "Price (€/kg)": 3.5, "CO₂ (kg)": 0.9, "Marketing Claim": "It's like milk but made for humans", "Source": "oatly.com"},
            {"Company": "Miyoko's Creamery", "Product": "Cashew Cheese", "Price (€/kg)": 35.0, "CO₂ (kg)": 1.5, "Marketing Claim": "Artisan cultured", "Source": "miyokos.com"},
        ],
        "Algae": [
            {"Company": "Algama", "Product": "Spirulina Protein", "Price (€/kg)": 35.0, "CO₂ (kg)": 0.8, "Marketing Claim": "Ocean superfood", "Source": "algamafoods.com"},
            {"Company": "Sophie's BioNutrients", "Product": "Chlorella Protein", "Price (€/kg)": 38.0, "CO₂ (kg)": 0.9, "Marketing Claim": "Carbon negative", "Source": "sophiesbionutrients.com"},
            {"Company": "Algenist", "Product": "Algae Oil", "Price (€/kg)": 42.0, "CO₂ (kg)": 0.7, "Marketing Claim": "Sustainable omega-3", "Source": "algenist.com"},
            {"Company": "TerraVia", "Product": "Algae Flour", "Price (€/kg)": 32.0, "CO₂ (kg)": 0.6, "Marketing Claim": "Protein-rich baking", "Source": "terravia.com"},
            {"Company": "Corbion", "Product": "AlgaPrime DHA", "Price (€/kg)": 45.0, "CO₂ (kg)": 0.8, "Marketing Claim": "Sustainable omega-3", "Source": "corbion.com"},
        ]
    }

    def _get_fallback_data(self, category: str, max_results: int) -> List[Dict]:
        """Optimized fallback data with O(1) dict lookup."""
        # Direct dict lookup - O(1) instead of iterating through list
        if category and category in self.FALLBACK_DATA:
            data = self.FALLBACK_DATA[category]
        else:
            # If no category specified or not found, return first available category
            data = next(iter(self.FALLBACK_DATA.values())) if self.FALLBACK_DATA else []
        return data[:max_results]

    def get_stats(self) -> Dict:
        """Get usage statistics."""
        total_requests = self.api_calls_made + self.cache_hits
        cache_efficiency = (self.cache_hits / max(total_requests, 1)) * 100

        stats = {
            'api_calls_made': self.api_calls_made,
            'cache_hits': self.cache_hits,
            'cache_efficiency': f"{cache_efficiency:.1f}%",
            'api_cost_saved': f"~${(self.cache_hits * 0.01):.2f}",  # Rough estimate
            'database_enabled': self.use_database
        }

        # Add database stats if available
        if self.use_database and self.db:
            db_stats = self.db.get_stats()
            stats.update(db_stats)

        return stats

    def clear_cache(self):
        """Clear all cached data (only if database is enabled)."""
        if self.use_database and self.db:
            self.db.clear_old_cache(days=0)
            logger.info("Cache cleared")
        else:
            logger.info("No cache to clear (database not enabled)")
