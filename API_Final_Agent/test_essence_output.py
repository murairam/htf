"""Test Essence pipeline output structure"""
import asyncio
import json
from api_final_agent.pipelines.essence_pipeline import run_essence_analysis

async def test():
    print("Testing Essence pipeline...")
    result = await run_essence_analysis(
        product_description='Plant-based chocolate spread',
        business_objective='Test analysis',
        domain='Plant-Based',
        segment='Flexitarian'
    )
    
    print("\n=== RESULT KEYS ===")
    print(json.dumps(list(result.keys()), indent=2))
    
    print("\n=== RESULT STRUCTURE ===")
    for key in result.keys():
        val = result[key]
        if isinstance(val, dict):
            print(f'{key}: dict with {len(val)} keys -> {list(val.keys())[:5]}')
        elif isinstance(val, list):
            print(f'{key}: list with {len(val)} items')
        else:
            print(f'{key}: {type(val).__name__} = {str(val)[:100]}')
    
    print("\n=== FULL RESULT (first 2000 chars) ===")
    print(json.dumps(result, indent=2, default=str)[:2000])

if __name__ == "__main__":
    asyncio.run(test())
