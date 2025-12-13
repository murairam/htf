# Testing Guide for essenceAI

## Overview

essenceAI uses **pytest** for automated testing with comprehensive coverage of all core modules.

## Quick Start

```bash
# Run all tests
./run_tests.sh

# Or use pytest directly
pytest tests/ -v

# Run with coverage report
./run_tests.sh coverage

# Run specific test file
pytest tests/test_database.py -v
```

## Test Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Shared fixtures and configuration
├── test_database.py         # Database module tests
├── test_product_parser.py   # Product URL parser tests
└── test_competitor_data.py  # Competitor intelligence tests
```

## Test Coverage

### 1. Database Module (`test_database.py`)

Tests the SQLite database layer for caching and persistence:

- ✅ Database initialization and table creation
- ✅ Adding competitor data
- ✅ Retrieving competitors by category
- ✅ Caching analysis results
- ✅ Cache expiration logic
- ✅ Product URL storage
- ✅ Database statistics
- ✅ Old cache cleanup

**Key Tests:**
```python
def test_database_initialization(test_db)
def test_add_competitor(test_db)
def test_cache_analysis(test_db)
def test_cache_expiration(test_db)
```

### 2. Product Parser Module (`test_product_parser.py`)

Tests URL parsing and product information extraction:

- ✅ Category detection (Plant-Based, Fermentation, Algae)
- ✅ Fallback parsing when URL fetch fails
- ✅ Text extraction helpers
- ✅ Product concept generation
- ✅ URL structure validation

**Key Tests:**
```python
def test_detect_category_plant_based(parser)
def test_fallback_parse(parser)
def test_create_product_concept(parser)
```

### 3. Competitor Intelligence Module (`test_competitor_data.py`)

Tests the optimized competitor data retrieval with caching:

- ✅ Module initialization
- ✅ Fallback data structure
- ✅ Data formatting
- ✅ Competitor caching
- ✅ Cache hit/miss tracking
- ✅ Usage statistics
- ✅ Cache efficiency calculation

**Key Tests:**
```python
def test_get_competitors_with_cache(intel)
def test_cache_competitors(intel)
def test_get_stats(intel)
```

## Running Tests

### Basic Test Run

```bash
cd essenceAI
pytest tests/ -v
```

### With Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

This generates:
- Terminal coverage summary
- HTML report in `htmlcov/index.html`

### Run Specific Tests

```bash
# Single test file
pytest tests/test_database.py -v

# Single test function
pytest tests/test_database.py::test_add_competitor -v

# Tests matching pattern
pytest tests/ -k "cache" -v
```

### Test Markers

```bash
# Run only unit tests (fast)
pytest tests/ -m unit -v

# Run integration tests
pytest tests/ -m integration -v

# Skip slow tests
pytest tests/ -m "not slow" -v
```

## Test Fixtures

### Shared Fixtures (conftest.py)

```python
@pytest.fixture
def test_db():
    """Creates a temporary test database"""
    # Automatically cleaned up after test

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mocks API keys for testing"""
    # No real API calls in tests
```

### Module-Specific Fixtures

Each test file has its own fixtures:

```python
# test_database.py
@pytest.fixture
def test_db():
    """Test database instance"""

# test_product_parser.py
@pytest.fixture
def parser():
    """Product parser instance"""

# test_competitor_data.py
@pytest.fixture
def intel(test_db_path):
    """Intelligence module with test DB"""
```

## Writing New Tests

### Test Template

```python
"""
Tests for new_module
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from new_module import NewClass


@pytest.fixture
def instance():
    """Create test instance"""
    return NewClass()


def test_basic_functionality(instance):
    """Test basic feature"""
    result = instance.do_something()
    assert result is not None
    assert isinstance(result, dict)


def test_error_handling(instance):
    """Test error cases"""
    with pytest.raises(ValueError):
        instance.do_invalid_thing()
```

## Continuous Integration

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
cd essenceAI
pytest tests/ --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### GitHub Actions (Future)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=src
```

## Test Best Practices

### ✅ DO:

1. **Test one thing per test**
   ```python
   def test_add_competitor():
       # Only test adding

   def test_retrieve_competitor():
       # Only test retrieval
   ```

2. **Use descriptive names**
   ```python
   def test_cache_returns_none_when_expired()
   def test_parser_detects_plant_based_category()
   ```

3. **Clean up resources**
   ```python
   @pytest.fixture
   def temp_db():
       db = create_db()
       yield db
       db.close()
       os.remove(db.path)
   ```

4. **Mock external dependencies**
   ```python
   @patch('requests.get')
   def test_api_call(mock_get):
       mock_get.return_value.json.return_value = {...}
   ```

### ❌ DON'T:

1. Don't make real API calls in tests
2. Don't depend on test execution order
3. Don't use production databases
4. Don't skip cleanup

## Debugging Failed Tests

### Verbose Output

```bash
pytest tests/ -vv --tb=long
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Run Last Failed Tests

```bash
pytest tests/ --lf
```

### Print Debug Output

```python
def test_something():
    result = function()
    print(f"Debug: {result}")  # Will show with -s flag
    assert result == expected

# Run with: pytest tests/ -s
```

## Coverage Goals

Target: **80%+ code coverage**

Current coverage by module:
- `database.py`: ~95%
- `product_parser.py`: ~85%
- `competitor_data_optimized.py`: ~90%
- `rag_engine_optimized.py`: Not yet tested (integration test needed)

## Integration Testing (Future)

For testing with real APIs (use sparingly):

```python
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("RUN_INTEGRATION"),
                    reason="Integration tests disabled")
def test_real_api_call():
    # Test with actual API
    pass
```

Run with:
```bash
RUN_INTEGRATION=1 pytest tests/ -m integration
```

## Performance Testing

```python
import time

def test_cache_performance():
    start = time.time()
    result = get_competitors(use_cache=True)
    duration = time.time() - start

    assert duration < 0.1  # Should be fast with cache
```

## Test Maintenance

- Run tests before every commit
- Update tests when changing functionality
- Add tests for bug fixes
- Review coverage reports monthly
- Keep test data minimal and focused

## Troubleshooting

### Import Errors

```bash
# Ensure src is in path
export PYTHONPATH="${PYTHONPATH}:./src"
pytest tests/
```

### Database Lock Errors

```python
# Use separate test databases
@pytest.fixture
def test_db():
    db_path = f"test_{uuid.uuid4()}.db"
    # ...
```

### Slow Tests

```bash
# Profile test execution
pytest tests/ --durations=10
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Guide](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Last Updated**: December 2024
**Maintainer**: essenceAI Team
