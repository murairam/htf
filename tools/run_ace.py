#!/usr/bin/env python3
"""
Run ACE pipeline and capture raw output.
Generates artifacts/ace/ace_raw.json
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

from api_final_agent.pipelines.ace_pipeline import run_ace_analysis

ARTIFACTS_DIR = project_root / "artifacts" / "ace"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    """Run ACE pipeline with test inputs."""
    # Get inputs from environment or use defaults
    barcode = os.getenv("TEST_BARCODE", "3017620422003")  # Nutella barcode as default
    business_objective = os.getenv("TEST_OBJECTIVE", "Increase flexitarian appeal")
    
    print("=" * 80)
    print("Running ACE Pipeline")
    print("=" * 80)
    print(f"Barcode: {barcode}")
    print(f"Business Objective: {business_objective}")
    print()
    
    if not barcode or barcode == "":
        print("❌ ERROR: TEST_BARCODE environment variable is required")
        print()
        print("Usage:")
        print("  TEST_BARCODE=3017620422003 TEST_OBJECTIVE='Your objective' python tools/run_ace.py")
        sys.exit(1)
    
    try:
        print("🔍 Running ACE analysis...")
        start_time = datetime.now()
        
        result = await run_ace_analysis(
            barcode=barcode,
            business_objective=business_objective
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✅ ACE analysis completed in {duration:.1f}s")
        print()
        
        # Save raw output
        output_file = ARTIFACTS_DIR / "ace_raw.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Raw output saved to: {output_file}")
        print(f"📊 Output keys: {list(result.keys())}")
        print()
        
        # Print summary
        print("Summary:")
        print(f"  - Total keys: {len(result)}")
        if "scoring_results" in result:
            scores = result.get("scoring_results", {}).get("scores", {})
            if scores:
                print(f"  - Global Score: {scores.get('global_score', 'N/A')}")
        if "product_information" in result:
            product_info = result.get("product_information", {}).get("basic_info", {})
            if product_info:
                print(f"  - Product: {product_info.get('name', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running ACE pipeline: {e}")
        import traceback
        traceback.print_exc()
        
        # Save error output
        error_output = {
            "error": str(e),
            "barcode": barcode,
            "business_objective": business_objective,
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc()
        }
        
        output_file = ARTIFACTS_DIR / "ace_raw_error.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(error_output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Error output saved to: {output_file}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

