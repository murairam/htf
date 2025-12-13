#!/usr/bin/env python3
"""Test Marketing Agent with all segments."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from agents import MarketingAgent


def test_marketing_agent():
    """Test marketing agent with all segments."""
    agent = MarketingAgent()
    
    segments = ['High Essentialist', 'Skeptic', 'Non-Consumer']
    
    for segment in segments:
        print(f"\n{'='*60}")
        print(f"Testing {segment}")
        print('='*60)
        
        result = agent.execute({
            'product_description': 'Plant-based burger for fast-food chains',
            'segment': segment,
            'domain': 'Plant-Based'
        })
        
        if result['status'] == 'success':
            data = result['data']
            print(f"✓ Status: {result['status']}")
            print(f"✓ Segment: {data['segment']}")
            print(f"✓ Primary Message: {data['messaging']['primary_message']}")
            print(f"✓ Channels: {len(data['channels'])}")
            print(f"✓ Tactics: {len(data['tactics'])}")
            print(f"✓ Key Messages: {len(data['key_messages'])}")
            
            # Show first tactic
            print(f"\nFirst Tactic:")
            print(f"  - {data['tactics'][0]['tactic']}")
            print(f"  - Goal: {data['tactics'][0]['goal']}")
        else:
            print(f"✗ Error: {result['error']}")
            return False
    
    print(f"\n{'='*60}")
    print("✓ All segments tested successfully!")
    print('='*60)
    return True


if __name__ == "__main__":
    success = test_marketing_agent()
    sys.exit(0 if success else 1)
