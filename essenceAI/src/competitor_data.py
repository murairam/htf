"""
Competitor Intelligence Module - Real-Time Data
Uses APIs and web search to fetch live competitor data.
"""

import os
import json
import requests
from typing import Dict, List, Optional
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class CompetitorIntelligence:
    """
    Fetches real-time competitor data using free APIs.
    """

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")  # Free tier available

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

    def search_competitors(self, category: str, query: str) -> List[Dict]:
        """
        Use Tavily API (free tier) to search for competitors.
        Falls back to OpenAI if Tavily not available.

        Args:
            category: "Precision Fermentation", "Plant-Based", or "Algae"
            query: Specific search query

        Returns:
            List of competitor data dictionaries
        """
        # Try Tavily first (better for structured data)
        if self.tavily_api_key:
            return self._search_with_tavily(category, query)
        else:
            # Fallback to OpenAI-powered search
            return self._search_with_openai(category, query)

    def _search_with_tavily(self, category: str, query: str) -> List[Dict]:
        """
        Search using Tavily API (free tier: 1000 requests/month).
        """
        try:
            url = "https://api.tavily.com/search"

            search_query = f"{category} companies {query} pricing market data 2024 2025"

            payload = {
                "api_key": self.tavily_api_key,
                "query": search_query,
                "search_depth": "advanced",
                "include_answer": True,
                "max_results": 5
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Parse results and extract competitor info
            competitors = self._parse_search_results(data.get("results", []), category)

            return competitors

        except Exception as e:
            print(f"Tavily search failed: {e}. Falling back to OpenAI...")
            return self._search_with_openai(category, query)

    def _search_with_openai(self, category: str, query: str) -> List[Dict]:
        """
        Use OpenAI to generate structured competitor data based on its knowledge.
        This uses your OpenAI credits.
        """
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.openai_api_key)

            prompt = f"""You are a market research analyst specializing in sustainable food innovation.

Task: Provide real, current competitor data for the {category} sector.

Query: {query}

Return a JSON array of 4-5 real companies with this exact structure:
[
  {{
    "Company": "Company Name",
    "Product": "Main product name",
    "Price_per_kg": estimated price in USD (realistic market price),
    "CO2_Emission_kg": estimated CO2 emissions per kg (realistic),
    "Marketing_Claim": their main marketing message,
    "Target_Market": their target market segment,
    "Year_Founded": year founded,
    "Website": company website URL
  }}
]

IMPORTANT:
- Use REAL companies that exist in 2024/2025
- Provide realistic price estimates based on current market data
- Include accurate CO2 emission estimates
- Only return valid JSON, no additional text"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a market research expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            content = response.choices[0].message.content

            # Handle if response is wrapped in json key
            try:
                parsed = json.loads(content)
                if "competitors" in parsed:
                    competitors = parsed["competitors"]
                elif isinstance(parsed, list):
                    competitors = parsed
                else:
                    # Assume the entire object is the array
                    competitors = list(parsed.values())[0] if parsed else []
            except json.JSONDecodeError:
                print(f"Failed to parse OpenAI response: {content}")
                competitors = []

            return competitors

        except Exception as e:
            print(f"OpenAI search failed: {e}")
            return self._get_fallback_data(category)

    def _parse_search_results(self, results: List[Dict], category: str) -> List[Dict]:
        """
        Parse Tavily search results into structured competitor data.
        Uses OpenAI to extract structured info from search snippets.
        """
        if not results:
            return self._get_fallback_data(category)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            # Combine search results
            search_context = "\n\n".join([
                f"Source: {r.get('title', 'Unknown')}\n{r.get('content', '')}"
                for r in results[:5]
            ])

            prompt = f"""Extract competitor information from these search results about {category} companies.

Search Results:
{search_context}

Return a JSON array of companies with this structure:
[
  {{
    "Company": "Company Name",
    "Product": "Main product",
    "Price_per_kg": estimated price in USD,
    "CO2_Emission_kg": estimated CO2 per kg,
    "Marketing_Claim": main claim,
    "Target_Market": target market,
    "Year_Founded": year,
    "Website": URL
  }}
]

Extract 3-5 companies. If exact data isn't available, provide reasonable estimates based on context."""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            # Extract array from response
            if isinstance(parsed, dict):
                competitors = list(parsed.values())[0] if parsed else []
            else:
                competitors = parsed

            return competitors if competitors else self._get_fallback_data(category)

        except Exception as e:
            print(f"Failed to parse search results: {e}")
            return self._get_fallback_data(category)

    def _get_fallback_data(self, category: str) -> List[Dict]:
        """
        Minimal fallback data if all APIs fail.
        """
        fallback = {
            "Precision Fermentation": [
                {"Company": "Perfect Day", "Product": "Animal-Free Whey", "Price_per_kg": 45.0,
                 "CO2_Emission_kg": 2.1, "Marketing_Claim": "Real dairy, no cows",
                 "Target_Market": "Dairy alternatives", "Year_Founded": 2014, "Website": "perfectday.com"}
            ],
            "Plant-Based": [
                {"Company": "Beyond Meat", "Product": "Plant-Based Burger", "Price_per_kg": 18.5,
                 "CO2_Emission_kg": 3.5, "Marketing_Claim": "Looks, cooks, tastes like beef",
                 "Target_Market": "Meat alternatives", "Year_Founded": 2009, "Website": "beyondmeat.com"}
            ],
            "Algae": [
                {"Company": "Algama", "Product": "Spirulina Protein", "Price_per_kg": 28.0,
                 "CO2_Emission_kg": 1.2, "Marketing_Claim": "Ocean-grown superfood",
                 "Target_Market": "Protein supplements", "Year_Founded": 2013, "Website": "algamafoods.com"}
            ]
        }
        return fallback.get(category, [])

    def get_data(self, category: str, query: Optional[str] = None) -> pd.DataFrame:
        """
        Get competitor data as DataFrame.

        Args:
            category: One of "Precision Fermentation", "Plant-Based", "Algae"
            query: Optional specific search query

        Returns:
            DataFrame with competitor data
        """
        if query is None:
            query = f"top companies market leaders"

        competitors = self.search_competitors(category, query)

        if not competitors:
            competitors = self._get_fallback_data(category)

        return pd.DataFrame(competitors)

    def get_market_stats(self, category: str) -> Dict:
        """
        Calculate market statistics.
        """
        df = self.get_data(category)

        if df.empty:
            return {"error": "No data available"}

        return {
            "avg_price_per_kg": round(df["Price_per_kg"].mean(), 2),
            "avg_co2_emission": round(df["CO2_Emission_kg"].mean(), 2),
            "competitor_count": len(df),
            "price_range": {
                "min": round(df["Price_per_kg"].min(), 2),
                "max": round(df["Price_per_kg"].max(), 2)
            }
        }
