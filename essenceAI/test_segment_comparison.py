#!/usr/bin/env python3
"""Test segment comparison functionality."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from agents import MarketingAgent


def test_segment_comparison():
    """Compare strategies across all segments."""
    agent = MarketingAgent()
    
    product = "Precision fermented artisan cheese"
    domain = "Precision Fermentation"
    
    print(f"\n{'='*60}")
    print(f"Comparing Segments for: {product}")
    print('='*60)
    
    result = agent.compare_segments(product, domain)
    
    if result['status'] == 'success':
        for segment, strategy in result['data'].items():
            print(f"\n📊 {segment}:")
            print(f"   Focus: {strategy['segment_profile']['messaging_focus']}")
            print(f"   Key Factors: {', '.join(strategy['segment_profile']['key_factors'][:2])}")
            print(f"   Top Tactic: {strategy['tactics'][0]['tactic']}")
            print(f"   Channels: {', '.join([c['channel'] for c in strategy['channels'][:2]])}")
        
        print(f"\n{'='*60}")
        print("✓ Segment comparison completed!")
        print('='*60)
        return True
    else:
        print(f"✗ Error: {result['error']}")
        return False


if __name__ == "__main__":
    success = test_segment_comparison()
    sys.exit(0 if success else 1)
