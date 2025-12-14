"""
Phase 1: Inspection Tool
Calls ACE_Framework and EssenceAI APIs to inspect their JSON outputs.
Saves raw responses and generates schema reports.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import traceback

# Configuration from environment variables
ACE_BASE_URL = os.getenv("ACE_BASE_URL", "http://localhost:8001")
ESSENCE_BASE_URL = os.getenv("ESSENCE_BASE_URL", "http://localhost:8002")
ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)


def save_json(data: Dict[str, Any], filename: str) -> Path:
    """Save JSON data to artifacts directory."""
    filepath = ARTIFACTS_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {filepath}")
    return filepath


def analyze_schema(data: Any, path: str = "", max_depth: int = 5) -> Dict[str, Any]:
    """
    Recursively analyze JSON structure to extract schema information.
    Returns a dict with keys, types, and sample values.
    """
    if max_depth <= 0:
        return {"type": "max_depth_reached", "path": path}
    
    if isinstance(data, dict):
        schema = {
            "type": "object",
            "path": path,
            "keys": {},
            "key_count": len(data)
        }
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            schema["keys"][key] = analyze_schema(value, new_path, max_depth - 1)
        return schema
    elif isinstance(data, list):
        schema = {
            "type": "array",
            "path": path,
            "length": len(data),
            "item_schema": None
        }
        if data:
            # Analyze first item as representative
            schema["item_schema"] = analyze_schema(data[0], f"{path}[0]", max_depth - 1)
        return schema
    else:
        return {
            "type": type(data).__name__,
            "path": path,
            "sample_value": str(data)[:100] if data is not None else None
        }


def generate_schema_report(samples: List[Dict[str, Any]], api_name: str) -> str:
    """
    Generate a markdown schema report from multiple sample responses.
    """
    report_lines = [
        f"# {api_name} API Schema Report",
        f"Generated: {datetime.now().isoformat()}",
        f"Number of samples analyzed: {len(samples)}",
        ""
    ]
    
    # Collect all unique keys across samples
    all_keys = set()
    key_types = {}
    key_examples = {}
    
    def collect_keys(data: Any, path: str = ""):
        """Recursively collect all keys and their types."""
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                all_keys.add(new_path)
                
                if isinstance(value, (dict, list)):
                    collect_keys(value, new_path)
                else:
                    value_type = type(value).__name__
                    if new_path not in key_types:
                        key_types[new_path] = value_type
                        key_examples[new_path] = str(value)[:100] if value is not None else None
        elif isinstance(data, list) and data:
            collect_keys(data[0], f"{path}[0]")
    
    for sample in samples:
        collect_keys(sample)
    
    # Generate report sections
    report_lines.extend([
        "## Top-Level Keys",
        ""
    ])
    
    top_level_keys = sorted([k for k in all_keys if '.' not in k])
    for key in top_level_keys:
        key_type = key_types.get(key, "unknown")
        example = key_examples.get(key, "N/A")
        report_lines.append(f"- `{key}`: {key_type}")
        if example and example != "None":
            report_lines.append(f"  - Example: `{example[:80]}...`" if len(example) > 80 else f"  - Example: `{example}`")
    
    report_lines.extend([
        "",
        "## Nested Keys (Dot Notation)",
        ""
    ])
    
    nested_keys = sorted([k for k in all_keys if '.' in k])
    for key in nested_keys:
        key_type = key_types.get(key, "unknown")
        example = key_examples.get(key, "N/A")
        report_lines.append(f"- `{key}`: {key_type}")
        if example and example != "None":
            report_lines.append(f"  - Example: `{example[:80]}...`" if len(example) > 80 else f"  - Example: `{example}`")
    
    # Add sample snippets
    report_lines.extend([
        "",
        "## Sample Response Snippet",
        "",
        "```json"
    ])
    
    if samples:
        # Show first sample, truncated
        sample_json = json.dumps(samples[0], indent=2, ensure_ascii=False)
        # Truncate if too long
        if len(sample_json) > 2000:
            sample_json = sample_json[:2000] + "\n... (truncated)"
        report_lines.append(sample_json)
    
    report_lines.extend([
        "```",
        ""
    ])
    
    return "\n".join(report_lines)


def call_ace_api(barcode: str, objectives: str = "") -> Optional[Dict[str, Any]]:
    """Call ACE_Framework API /run-analysis endpoint."""
    url = f"{ACE_BASE_URL}/run-analysis"
    
    # Generate a dummy analysis_id for testing
    import uuid
    analysis_id = str(uuid.uuid4())
    
    payload = {
        "analysis_id": analysis_id,
        "barcode": barcode,
        "objectives": objectives
    }
    
    try:
        print(f"📞 Calling ACE API: {url}")
        print(f"   Payload: barcode={barcode}, objectives={objectives[:50]}...")
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ ACE API response received ({len(str(result))} chars)")
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ ACE API error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Error detail: {error_detail}")
            except:
                print(f"   Status code: {e.response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error calling ACE API: {e}")
        traceback.print_exc()
        return None


def call_essence_api(product_link: Optional[str] = None, product_description: Optional[str] = None, 
                     business_objective: str = "") -> Optional[Dict[str, Any]]:
    """Call EssenceAI API endpoint."""
    url = f"{ESSENCE_BASE_URL}/analyze"
    
    payload = {
        "business_objective": business_objective
    }
    
    if product_link:
        payload["product_link"] = product_link
    elif product_description:
        payload["product_description"] = product_description
    else:
        print("❌ EssenceAI requires either product_link or product_description")
        return None
    
    try:
        print(f"📞 Calling EssenceAI API: {url}")
        print(f"   Payload: {list(payload.keys())}")
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ EssenceAI API response received ({len(str(result))} chars)")
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ EssenceAI API error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Error detail: {error_detail}")
            except:
                print(f"   Status code: {e.response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error calling EssenceAI API: {e}")
        traceback.print_exc()
        return None


def run_inspection():
    """Run inspection scenarios for both APIs."""
    print("=" * 80)
    print("Phase 1: API Output Inspection")
    print("=" * 80)
    print()
    
    ace_samples = []
    essence_samples = []
    
    # ACE API Test Scenarios
    print("\n" + "=" * 80)
    print("ACE_Framework API Tests")
    print("=" * 80)
    
    ace_scenarios = [
        {
            "name": "Valid barcode + short objective",
            "barcode": "3017620422003",  # Nutella
            "objectives": "Increase flexitarian appeal"
        },
        {
            "name": "Valid barcode + long objective",
            "barcode": "3017620422003",
            "objectives": "Increase flexitarian appeal by improving packaging design, reducing greenwashing perception, and enhancing naturalness cues. Target consumers who are curious about plant-based alternatives but hesitant to fully commit."
        },
        {
            "name": "Invalid barcode (not found)",
            "barcode": "9999999999999",
            "objectives": "Test error handling"
        }
    ]
    
    for i, scenario in enumerate(ace_scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        result = call_ace_api(scenario['barcode'], scenario['objectives'])
        
        if result:
            filename = f"ace_sample_{i}.json"
            save_json(result, filename)
            ace_samples.append(result)
        else:
            # Save error response
            error_result = {
                "scenario": scenario['name'],
                "error": "API call failed",
                "barcode": scenario['barcode'],
                "objectives": scenario['objectives']
            }
            filename = f"ace_sample_{i}_error.json"
            save_json(error_result, filename)
    
    # EssenceAI API Test Scenarios
    print("\n" + "=" * 80)
    print("EssenceAI API Tests")
    print("=" * 80)
    
    essence_scenarios = [
        {
            "name": "Valid product_link + objective",
            "product_link": "https://www.openfoodfacts.org/product/3017620422003/nutella",
            "product_description": None,
            "business_objective": "Increase market share in plant-based segment"
        },
        {
            "name": "Product description + objective",
            "product_link": None,
            "product_description": "Plant-based chocolate spread made from hazelnuts and cocoa",
            "business_objective": "Improve packaging and marketing strategy"
        },
        {
            "name": "Invalid link / empty description",
            "product_link": "https://invalid-url-that-does-not-exist.com",
            "product_description": None,
            "business_objective": "Test error handling"
        }
    ]
    
    for i, scenario in enumerate(essence_scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        result = call_essence_api(
            product_link=scenario['product_link'],
            product_description=scenario['product_description'],
            business_objective=scenario['business_objective']
        )
        
        if result:
            filename = f"essence_sample_{i}.json"
            save_json(result, filename)
            essence_samples.append(result)
        else:
            # Save error response
            error_result = {
                "scenario": scenario['name'],
                "error": "API call failed",
                "product_link": scenario['product_link'],
                "product_description": scenario['product_description'],
                "business_objective": scenario['business_objective']
            }
            filename = f"essence_sample_{i}_error.json"
            save_json(error_result, filename)
    
    # Generate schema reports
    print("\n" + "=" * 80)
    print("Generating Schema Reports")
    print("=" * 80)
    
    if ace_samples:
        ace_report = generate_schema_report(ace_samples, "ACE_Framework")
        report_path = ARTIFACTS_DIR / "ace_schema_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(ace_report)
        print(f"✅ Generated: {report_path}")
    else:
        print("⚠️  No ACE samples to analyze")
    
    if essence_samples:
        essence_report = generate_schema_report(essence_samples, "EssenceAI")
        report_path = ARTIFACTS_DIR / "essence_schema_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(essence_report)
        print(f"✅ Generated: {report_path}")
    else:
        print("⚠️  No EssenceAI samples to analyze")
    
    print("\n" + "=" * 80)
    print("✅ Inspection Complete!")
    print(f"📁 Artifacts saved to: {ARTIFACTS_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    run_inspection()

