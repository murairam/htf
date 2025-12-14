#!/usr/bin/env python3
"""
Run Essence pipeline and capture raw output.
Generates artifacts/essence/essence_raw.json
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add API_Final_Agent to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "API_Final_Agent"))

from api_final_agent.pipelines.essence_pipeline import run_essence_analysis

ARTIFACTS_DIR = project_root / "artifacts" / "essence"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    """Run Essence pipeline with test inputs."""
    # Get inputs from environment or use defaults
    product_link = os.getenv("TEST_PRODUCT_LINK")
    product_description = os.getenv("TEST_PRODUCT_DESCRIPTION", 
        "Plant-based chocolate spread made from hazelnuts and cocoa, suitable for vegans")
    business_objective = os.getenv("TEST_OBJECTIVE", "Increase market share in plant-based segment")
    domain = os.getenv("TEST_DOMAIN")
    segment = os.getenv("TEST_SEGMENT")
    
    print("=" * 80)
    print("Running Essence Pipeline")
    print("=" * 80)
    print(f"Product Link: {product_link or 'None'}")
    print(f"Product Description: {product_description[:80] if product_description else 'None'}...")
    print(f"Business Objective: {business_objective}")
    print(f"Domain: {domain or 'None'}")
    print(f"Segment: {segment or 'None'}")
    print()
    
    if not product_link and not product_description:
        print("❌ ERROR: Either TEST_PRODUCT_LINK or TEST_PRODUCT_DESCRIPTION must be provided")
        print()
        print("Usage:")
        print("  TEST_PRODUCT_LINK='https://...' TEST_OBJECTIVE='Your objective' python tools/run_essence.py")
        print("  OR")
        print("  TEST_PRODUCT_DESCRIPTION='Product description' TEST_OBJECTIVE='Your objective' python tools/run_essence.py")
        sys.exit(1)
    
    try:
        print("🔍 Running Essence analysis...")
        start_time = datetime.now()
        
        result = await run_essence_analysis(
            product_link=product_link,
            product_description=product_description,
            business_objective=business_objective,
            domain=domain,
            segment=segment
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✅ Essence analysis completed in {duration:.1f}s")
        print()
        
        # Save raw output
        output_file = ARTIFACTS_DIR / "essence_raw.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Raw output saved to: {output_file}")
        print(f"📊 Output keys: {list(result.keys())}")
        print()
        
        # Print summary
        print("Summary:")
        print(f"  - Total keys: {len(result)}")
        if "status" in result:
            print(f"  - Status: {result.get('status')}")
        if "workflow" in result:
            workflow = result.get("workflow", {})
            if "steps" in workflow:
                print(f"  - Workflow steps: {len(workflow['steps'])}")
        if "competitor_analysis" in result:
            print(f"  - Competitor analysis: Present")
        if "research_insights" in result:
            print(f"  - Research insights: Present")
        if "marketing_strategy" in result:
            print(f"  - Marketing strategy: Present")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running Essence pipeline: {e}")
        import traceback
        traceback.print_exc()
        
        # Save error output
        error_output = {
            "error": str(e),
            "product_link": product_link,
            "product_description": product_description,
            "business_objective": business_objective,
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }
        
        output_file = ARTIFACTS_DIR / "essence_raw_error.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(error_output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Error output saved to: {output_file}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

