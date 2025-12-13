"""
Persistent Database for essenceAI
Stores competitor data, analysis results, and product information.
This reduces API calls by caching results.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


class EssenceAIDatabase:
    """
    SQLite database for storing analysis results and competitor data.
    """

    def __init__(self, db_path: str = "essenceai.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Create database tables if they don't exist."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        cursor = self.conn.cursor()

        # Table for competitor data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                category TEXT NOT NULL,
                product_type TEXT,
                price_per_kg REAL,
                co2_emission REAL,
                marketing_claim TEXT,
                source_url TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(company_name, product_type)
            )
        """)

        # Table for analysis results (cached)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                product_concept TEXT NOT NULL,
                category TEXT NOT NULL,
                segment TEXT,
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table for product URLs (for parsing Carrefour, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                product_name TEXT,
                brand TEXT,
                category TEXT,
                price REAL,
                parsed_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance optimization
        # Index on category for fast competitor lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_competitors_category
            ON competitors(category)
        """)

        # Index on last_updated for cache validation
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_competitors_last_updated
            ON competitors(last_updated)
        """)

        # Composite index for filtered cache queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_cache_category_created
            ON analysis_cache(category, created_at)
        """)

        # Index on created_at for cache cleanup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_cache_created_at
            ON analysis_cache(created_at)
        """)

        # Index on product_urls created_at
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_urls_created_at
            ON product_urls(created_at)
        """)

        self.conn.commit()

    def add_competitor(self, data: Dict) -> int:
        """
        Add or update competitor data.

        Args:
            data: Dictionary with competitor information

        Returns:
            Row ID of inserted/updated competitor
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO competitors
            (company_name, category, product_type, price_per_kg, co2_emission,
             marketing_claim, source_url, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data.get('company_name'),
            data.get('category'),
            data.get('product_type'),
            data.get('price_per_kg'),
            data.get('co2_emission'),
            data.get('marketing_claim'),
            data.get('source_url')
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_competitors(self, category: str, limit: int = 10) -> List[Dict]:
        """
        Get competitors for a category.

        Args:
            category: Product category
            limit: Maximum number of results

        Returns:
            List of competitor dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM competitors
            WHERE category = ?
            ORDER BY last_updated DESC
            LIMIT ?
        """, (category, limit))

        return [dict(row) for row in cursor.fetchall()]

    def cache_analysis(self, product_concept: str, category: str,
                      segment: str, result: Dict) -> None:
        """
        Cache analysis result to avoid repeated API calls.

        Args:
            product_concept: Product description
            category: Product category
            segment: Consumer segment
            result: Analysis result dictionary
        """
        # Create hash for deduplication
        query_str = f"{product_concept}|{category}|{segment}"
        query_hash = hashlib.md5(query_str.encode()).hexdigest()

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO analysis_cache
            (query_hash, product_concept, category, segment, result_json, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (query_hash, product_concept, category, segment, json.dumps(result)))

        self.conn.commit()

    def get_cached_analysis(self, product_concept: str, category: str,
                           segment: str, max_age_hours: int = 24) -> Optional[Dict]:
        """
        Get cached analysis if it exists and is recent.

        Args:
            product_concept: Product description
            category: Product category
            segment: Consumer segment
            max_age_hours: Maximum age of cache in hours

        Returns:
            Cached result or None
        """
        query_str = f"{product_concept}|{category}|{segment}"
        query_hash = hashlib.md5(query_str.encode()).hexdigest()

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT result_json, created_at FROM analysis_cache
            WHERE query_hash = ?
            AND datetime(created_at) > datetime('now', '-' || ? || ' hours')
        """, (query_hash, max_age_hours))

        row = cursor.fetchone()
        if row:
            print(f"💾 Found cached analysis from {row['created_at']}")
            return json.loads(row['result_json'])
        return None

    def add_product_url(self, url: str, parsed_data: Dict) -> int:
        """
        Store parsed product URL data.

        Args:
            url: Product URL
            parsed_data: Extracted product information

        Returns:
            Row ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO product_urls
            (url, product_name, brand, category, price, parsed_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            url,
            parsed_data.get('product_name'),
            parsed_data.get('brand'),
            parsed_data.get('category'),
            parsed_data.get('price'),
            json.dumps(parsed_data)
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_product_by_url(self, url: str) -> Optional[Dict]:
        """
        Get cached product data by URL.

        Args:
            url: Product URL

        Returns:
            Product data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM product_urls WHERE url = ?
        """, (url,))

        row = cursor.fetchone()
        if row:
            data = dict(row)
            data['parsed_data'] = json.loads(data['parsed_data'])
            return data
        return None

    def get_stats(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.cursor()

        stats = {}

        # Count competitors
        cursor.execute("SELECT COUNT(*) as count FROM competitors")
        stats['total_competitors'] = cursor.fetchone()['count']

        # Count cached analyses
        cursor.execute("SELECT COUNT(*) as count FROM analysis_cache")
        stats['cached_analyses'] = cursor.fetchone()['count']

        # Count product URLs
        cursor.execute("SELECT COUNT(*) as count FROM product_urls")
        stats['product_urls'] = cursor.fetchone()['count']

        return stats

    def clear_old_cache(self, days: int = 7):
        """
        Clear cache older than specified days.

        Args:
            days: Age threshold in days
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM analysis_cache
            WHERE datetime(created_at) < datetime('now', '-' || ? || ' days')
        """, (days,))

        deleted = cursor.rowcount
        self.conn.commit()
        print(f"🗑️ Deleted {deleted} old cache entries")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.close()
        return False

    def __del__(self):
        """Destructor - cleanup connection if not already closed."""
        self.close()
