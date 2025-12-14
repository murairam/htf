#!/usr/bin/env python3
"""
Run both ACE and Essence pipelines, then generate unified output.
Generates:
- artifacts/ace/ace_raw.json
- artifacts/essence/essence_raw.json
- artifacts/final/unified.json
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
from api_final_agent.pipelines.essence_pipeline import run_essence_analysis
from api_final_agent.unified_output import create_unified_output

ACE_ARTIFACTS = project_root / "artifacts" / "ace"
ESSENCE_ARTIFACTS = project_root / "artifacts" / "essence"
FINAL_ARTIFACTS = project_root / "artifacts" / "final"

for dir_path in [ACE_ARTIFACTS, ESSENCE_ARTIFACTS, FINAL_ARTIFACTS]:
    dir_path.mkdir(parents=True, exist_ok=True)


async def main():
    """Run both pipelines and generate unified output."""
    # Get inputs from environment
    barcode = os.getenv("TEST_BARCODE")
    product_link = os.getenv("TEST_PRODUCT_LINK")
    product_description = os.getenv("TEST_PRODUCT_DESCRIPTION")
    business_objective = os.getenv("TEST_OBJECTIVE", "Comprehensive analysis")
    domain = os.getenv("TEST_DOMAIN")
    segment = os.getenv("TEST_SEGMENT")
    
    print("=" * 80)
    print("Running Both Pipelines (ACE + Essence)")
    print("=" * 80)
    print(f"Barcode: {barcode or 'None'}")
    print(f"Product Link: {product_link or 'None'}")
    print(f"Product Description: {product_description[:80] if product_description else 'None'}...")
    print(f"Business Objective: {business_objective}")
    print()
    
    if not barcode and not product_link and not product_description:
        print("❌ ERROR: At least one input must be provided")
        print()
        print("Usage:")
        print("  TEST_BARCODE=... TEST_PRODUCT_DESCRIPTION='...' TEST_OBJECTIVE='...' python tools/run_both.py")
        sys.exit(1)
    
    ace_result = None
    essence_result = None
    errors = []
    
    # Run ACE if barcode provided
    if barcode:
        try:
            print("📦 Running ACE pipeline...")
            ace_result = await run_ace_analysis(
                barcode=barcode,
                business_objective=business_objective
            )
            
            # Save ACE output
            ace_file = ACE_ARTIFACTS / "ace_raw.json"
            with open(ace_file, 'w', encoding='utf-8') as f:
                json.dump(ace_result, f, indent=2, ensure_ascii=False)
            print(f"✅ ACE output saved to: {ace_file}")
            
        except Exception as e:
            error_msg = f"ACE pipeline failed: {str(e)}"
            errors.append({"source": "ace", "error": error_msg})
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
    
    # Run Essence if link or description provided
    if product_link or product_description:
        try:
            print("🌱 Running Essence pipeline...")
            essence_result = await run_essence_analysis(
                product_link=product_link,
                product_description=product_description,
                business_objective=business_objective,
                domain=domain,
                segment=segment
            )
            
            # Save Essence output
            essence_file = ESSENCE_ARTIFACTS / "essence_raw.json"
            with open(essence_file, 'w', encoding='utf-8') as f:
                json.dump(essence_result, f, indent=2, ensure_ascii=False)
            print(f"✅ Essence output saved to: {essence_file}")
            
        except Exception as e:
            error_msg = f"Essence pipeline failed: {str(e)}"
            errors.append({"source": "essence", "error": error_msg})
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
    
    # Determine status
    ace_ok = ace_result is not None
    essence_ok = essence_result is not None
    
    if ace_ok and essence_ok:
        status = "ok"
    elif ace_ok or essence_ok:
        status = "partial"
    else:
        status = "error"
    
    # Generate unified output
    print()
    print("🔗 Generating unified output...")
    analysis_id = str(datetime.now().timestamp())
    
    unified_output = create_unified_output(
        analysis_id=analysis_id,
        input_data={
            "business_objective": business_objective,
            "barcode": barcode,
            "product_link": product_link,
            "product_description": product_description,
            "domain": domain,
            "segment": segment
        },
        ace_result=ace_result,
        essence_result=essence_result,
        status=status,
        errors=errors
    )
    
    # Save unified output
    unified_file = FINAL_ARTIFACTS / "unified.json"
    with open(unified_file, 'w', encoding='utf-8') as f:
        json.dump(unified_output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Unified output saved to: {unified_file}")
    print()
    print("Summary:")
    print(f"  - Status: {status}")
    print(f"  - ACE: {'✅' if ace_ok else '❌'}")
    print(f"  - Essence: {'✅' if essence_ok else '❌'}")
    print(f"  - Errors: {len(errors)}")
    print(f"  - Unified keys: {len(unified_output)}")
    if "merged" in unified_output:
        print(f"  - Merged keys: {len(unified_output.get('merged', {}))}")
    if "raw_sources" in unified_output:
        raw = unified_output.get("raw_sources", {})
        print(f"  - Raw sources ACE: {'✅' if raw.get('ace') else '❌'}")
        print(f"  - Raw sources Essence: {'✅' if raw.get('essence') else '❌'}")


if __name__ == "__main__":
    asyncio.run(main())

