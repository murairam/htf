"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import sys
from pathlib import Path

# Add src to path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(autouse=True)
def cleanup_test_databases():
    """Cleanup test databases after each test"""
    yield
    # Cleanup any test database files
    test_dbs = [
        "test_essenceai.db",
        "test_competitors.db"
    ]
    for db_file in test_dbs:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except:
                pass


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-456")
    monkeypatch.setenv("TAVILY_API_KEY", "test-key-789")
