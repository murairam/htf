"""
Internal Investigation Tool
Runs ACE and Essence pipelines internally to capture raw outputs.
Phase 2: Understanding output structures before creating unified format.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from api_final_agent.pipelines.ace_pipeline import run_ace_analysis
from api_final_agent.pipelines.essence_pipeline import run_essence_analysis

ARTIFACTS_DIR = Path(__file__).parent.parent.parent / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)


def analyze_schema(data: Any, path: str = "", max_depth: int = 5) -> Dict[str, Any]:
    """
    Recursively analyze JSON structure to extract schema information.
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
            schema["item_schema"] = analyze_schema(data[0], f"{path}[0]", max_depth - 1)
        return schema
    else:
        return {
            "type": type(data).__name__,
            "path": path,
            "sample_value": str(data)[:100] if data is not None else None
        }


def generate_schema_report(samples: List[Dict[str, Any]], pipeline_name: str) -> str:
    """Generate markdown schema report from sample responses."""
    report_lines = [
        f"# {pipeline_name} Pipeline Schema Report",
        f"Generated: {datetime.now().isoformat()}",
        f"Number of samples analyzed: {len(samples)}",
        ""
    ]
    
    # Collect all unique keys
    all_keys = set()
    key_types = {}
    key_examples = {}
    
    def collect_keys(data: Any, path: str = ""):
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
    
    # Top-level keys
    report_lines.extend(["## Top-Level Keys", ""])
    top_level_keys = sorted([k for k in all_keys if '.' not in k])
    for key in top_level_keys:
        key_type = key_types.get(key, "unknown")
        example = key_examples.get(key, "N/A")
        report_lines.append(f"- `{key}`: {key_type}")
        if example and example != "None":
            report_lines.append(f"  - Example: `{example[:80]}...`" if len(example) > 80 else f"  - Example: `{example}`")
    
    # Nested keys
    report_lines.extend(["", "## Nested Keys (Dot Notation)", ""])
    nested_keys = sorted([k for k in all_keys if '.' in k])
    for key in nested_keys:
        key_type = key_types.get(key, "unknown")
        example = key_examples.get(key, "N/A")
        report_lines.append(f"- `{key}`: {key_type}")
        if example and example != "None":
            report_lines.append(f"  - Example: `{example[:80]}...`" if len(example) > 80 else f"  - Example: `{example}`")
    
    # Sample snippet
    report_lines.extend(["", "## Sample Response Snippet", "", "```json"])
    if samples:
        sample_json = json.dumps(samples[0], indent=2, ensure_ascii=False)
        if len(sample_json) > 2000:
            sample_json = sample_json[:2000] + "\n... (truncated)"
        report_lines.append(sample_json)
    report_lines.extend(["```", ""])
    
    return "\n".join(report_lines)


async def investigate_outputs() -> Dict[str, Any]:
    """
    Run internal investigation of ACE and Essence pipelines.
    Captures raw outputs and generates schema reports.
    """
    print("=" * 80)
    print("Phase 2: Internal Pipeline Investigation")
    print("=" * 80)
    print()
    
    ace_samples = []
    essence_samples = []
    
    # ACE Investigation Scenarios
    print("\n" + "=" * 80)
    print("ACE Pipeline Investigation")
    print("=" * 80)
    
    ace_scenarios = [
        {
            "name": "Valid barcode + short objective",
            "barcode": "3017620422003",
            "business_objective": "Increase flexitarian appeal"
        },
        {
            "name": "Valid barcode + long objective",
            "barcode": "3017620422003",
            "business_objective": "Increase flexitarian appeal by improving packaging design, reducing greenwashing perception, and enhancing naturalness cues."
        }
    ]
    
    for i, scenario in enumerate(ace_scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        try:
            result = await run_ace_analysis(
                barcode=scenario['barcode'],
                business_objective=scenario['business_objective']
            )
            filename = f"ace_raw_{i}.json"
            filepath = ARTIFACTS_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved: {filepath}")
            ace_samples.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            error_result = {
                "scenario": scenario['name'],
                "error": str(e),
                "barcode": scenario['barcode'],
                "business_objective": scenario['business_objective']
            }
            filename = f"ace_raw_{i}_error.json"
            filepath = ARTIFACTS_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2, ensure_ascii=False)
    
    # Essence Investigation Scenarios
    print("\n" + "=" * 80)
    print("Essence Pipeline Investigation")
    print("=" * 80)
    
    essence_scenarios = [
        {
            "name": "Product description + objective",
            "product_description": "Plant-based chocolate spread made from hazelnuts and cocoa",
            "business_objective": "Increase market share in plant-based segment"
        },
        {
            "name": "Product link + objective",
            "product_link": "https://www.openfoodfacts.org/product/3017620422003/nutella",
            "business_objective": "Improve packaging and marketing strategy"
        }
    ]
    
    for i, scenario in enumerate(essence_scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        try:
            result = await run_essence_analysis(
                product_link=scenario.get('product_link'),
                product_description=scenario.get('product_description'),
                business_objective=scenario['business_objective']
            )
            filename = f"essence_raw_{i}.json"
            filepath = ARTIFACTS_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved: {filepath}")
            essence_samples.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            error_result = {
                "scenario": scenario['name'],
                "error": str(e)
            }
            filename = f"essence_raw_{i}_error.json"
            filepath = ARTIFACTS_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2, ensure_ascii=False)
    
    # Generate schema reports
    print("\n" + "=" * 80)
    print("Generating Schema Reports")
    print("=" * 80)
    
    if ace_samples:
        ace_report = generate_schema_report(ace_samples, "ACE")
        report_path = ARTIFACTS_DIR / "ace_schema_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(ace_report)
        print(f"✅ Generated: {report_path}")
    
    if essence_samples:
        essence_report = generate_schema_report(essence_samples, "Essence")
        report_path = ARTIFACTS_DIR / "essence_schema_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(ace_report)
        print(f"✅ Generated: {report_path}")
    
    print("\n" + "=" * 80)
    print("✅ Investigation Complete!")
    print(f"📁 Artifacts saved to: {ARTIFACTS_DIR}")
    print("=" * 80)
    
    return {
        "ace_samples": len(ace_samples),
        "essence_samples": len(essence_samples),
        "artifacts_dir": str(ARTIFACTS_DIR)
    }

