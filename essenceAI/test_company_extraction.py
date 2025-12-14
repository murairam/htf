"""
Test AI-powered company name extraction
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from competitor_data import OptimizedCompetitorIntelligence

def test_company_extraction():
    """Test the AI-powered company name extraction"""

    print("=" * 80)
    print("TESTING AI-POWERED COMPANY NAME EXTRACTION")
    print("=" * 80)

    # Initialize
    comp_intel = OptimizedCompetitorIntelligence(use_database=False)

    # Test cases
    test_cases = [
        "Plant-based artisan cheese for European market",
        "Beyond Meat plant-based burger",
        "Precision fermented whey protein",
        "Oatly oat milk for coffee shops",
        "La Vie bacon alternative",
        "Impossible Foods burger patties",
        "Sustainable food alternatives",
        "Miyoko's Creamery cashew cheese",
        "Artisan plant-based products",
        "Perfect Day whey protein",
    ]

    print("\nTesting company name extraction:\n")

    for i, test_case in enumerate(test_cases, 1):
        company = comp_intel._extract_company_name(test_case)

        if company:
            print(f"{i}. ✅ '{test_case}'")
            print(f"   → Company found: '{company}'")
        else:
            print(f"{i}. ⭕ '{test_case}'")
            print(f"   → No company name detected")
        print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_company_extraction()
