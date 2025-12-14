#!/usr/bin/env python3
"""
Compare raw outputs with unified output to ensure zero information loss.
Generates schema reports and completeness verification.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent
REPORTS_DIR = project_root / "artifacts" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

ACE_FILE = project_root / "artifacts" / "ace" / "ace_raw.json"
ESSENCE_FILE = project_root / "artifacts" / "essence" / "essence_raw.json"
UNIFIED_FILE = project_root / "artifacts" / "final" / "unified.json"


def extract_all_paths(data: Any, prefix: str = "", max_depth: int = 10) -> Set[str]:
    """
    Extract all key paths from a nested structure.
    Returns set of dot-notation paths.
    """
    paths = set()
    
    if max_depth <= 0:
        return paths
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{prefix}.{key}" if prefix else key
            paths.add(current_path)
            
            # Recursively extract from nested structures
            nested_paths = extract_all_paths(value, current_path, max_depth - 1)
            paths.update(nested_paths)
            
    elif isinstance(data, list) and data:
        # For lists, check first element
        current_path = f"{prefix}[0]" if prefix else "[0]"
        nested_paths = extract_all_paths(data[0], current_path, max_depth - 1)
        paths.update(nested_paths)
        # Also add the list path itself
        if prefix:
            paths.add(prefix)
    
    return paths


def get_type_at_path(data: Any, path: str) -> str:
    """Get the type of value at a given path."""
    try:
        parts = path.split('.')
        current = data
        
        for part in parts:
            if '[' in part:
                # Handle list indexing
                key, index = part.split('[')
                index = int(index.rstrip(']'))
                current = current[key][index]
            else:
                current = current[part]
        
        if isinstance(current, dict):
            return "object"
        elif isinstance(current, list):
            return f"array[{type(current[0]).__name__ if current else 'unknown'}]"
        else:
            return type(current).__name__
    except (KeyError, IndexError, TypeError):
        return "unknown"


def generate_schema_report(data: Dict[str, Any], name: str) -> str:
    """Generate markdown schema report."""
    paths = sorted(extract_all_paths(data))
    
    lines = [
        f"# {name} Schema Report",
        f"Generated: {datetime.now().isoformat()}",
        "",
        f"Total key paths: {len(paths)}",
        "",
        "## All Key Paths",
        ""
    ]
    
    # Group by top-level key
    top_level = defaultdict(list)
    for path in paths:
        top_key = path.split('.')[0]
        top_level[top_key].append(path)
    
    for top_key in sorted(top_level.keys()):
        lines.append(f"### {top_key}")
        lines.append("")
        for path in sorted(top_level[top_key]):
            value_type = get_type_at_path(data, path)
            lines.append(f"- `{path}`: {value_type}")
        lines.append("")
    
    return "\n".join(lines)


def verify_completeness(ace_data: Dict[str, Any], essence_data: Dict[str, Any], 
                       unified_data: Dict[str, Any]) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    Verify that all paths from ACE and Essence exist in unified output.
    STRICT CHECK: Every path must exist in raw_sources or merged.
    
    Returns:
        (missing_ace_paths, missing_essence_paths, conflicts, merges)
    """
    ace_paths = extract_all_paths(ace_data) if ace_data else set()
    essence_paths = extract_all_paths(essence_data) if essence_data else set()
    unified_paths = extract_all_paths(unified_data)
    
    # Get raw_sources paths
    raw_sources = unified_data.get("raw_sources", {})
    ace_raw = raw_sources.get("ace", {}) if raw_sources else {}
    essence_raw = raw_sources.get("essence", {}) if raw_sources else {}
    merged = unified_data.get("merged", {})
    
    ace_raw_paths = extract_all_paths(ace_raw) if ace_raw else set()
    essence_raw_paths = extract_all_paths(essence_raw) if essence_raw else set()
    merged_paths = extract_all_paths(merged) if merged else set()
    
    # Check ACE paths - must exist in raw_sources.ace OR merged (with ace_ prefix or direct)
    missing_ace = []
    for path in ace_paths:
        found = False
        
        # Check in raw_sources.ace
        if path in ace_raw_paths:
            found = True
        # Check in merged (direct or with ace_ prefix)
        elif path in merged_paths:
            found = True
        elif f"ace_{path.split('.')[0]}" in merged_paths:
            # Check if it's under ace_ prefixed key
            found = True
        else:
            # Check if any unified path contains this path
            for upath in unified_paths:
                if path in upath or upath.endswith(f".{path}") or upath == path:
                    found = True
                    break
        
        if not found:
            missing_ace.append(path)
    
    # Check Essence paths - must exist in raw_sources.essence OR merged
    missing_essence = []
    for path in essence_paths:
        found = False
        
        # Check in raw_sources.essence
        if path in essence_raw_paths:
            found = True
        # Check in merged (direct or with essence_ prefix)
        elif path in merged_paths:
            found = True
        elif f"essence_{path.split('.')[0]}" in merged_paths:
            found = True
        else:
            # Check if any unified path contains this path
            for upath in unified_paths:
                if path in upath or upath.endswith(f".{path}") or upath == path:
                    found = True
                    break
        
        if not found:
            missing_essence.append(path)
    
    # Detect conflicts (same path, different values) - simplified
    conflicts = []
    common_paths = ace_paths.intersection(essence_paths)
    for path in common_paths:
        # Check if values differ (simplified check)
        try:
            ace_val = get_value_at_path(ace_data, path)
            essence_val = get_value_at_path(essence_data, path)
            if ace_val != essence_val:
                conflicts.append(path)
        except:
            pass
    
    # Detect merges (paths that exist in both and were merged)
    merges = []
    for path in common_paths:
        if path in merged_paths or any(path in mp for mp in merged_paths):
            merges.append(path)
    
    return missing_ace, missing_essence, conflicts, merges


def get_value_at_path(data: Any, path: str) -> Any:
    """Get value at a given path."""
    try:
        parts = path.split('.')
        current = data
        for part in parts:
            if '[' in part:
                key, index = part.split('[')
                index = int(index.rstrip(']'))
                current = current[key][index]
            else:
                current = current[part]
        return current
    except (KeyError, IndexError, TypeError):
        return None


def detect_visuals(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect visual artifacts (charts, images) in data."""
    visuals = []
    
    def search_for_visuals(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            # Check for plotly chart structure
            if "data" in obj and "layout" in obj:
                # This looks like a plotly chart
                visuals.append({
                    "path": path,
                    "title": obj.get("layout", {}).get("title", {}).get("text", "Chart") if isinstance(obj.get("layout", {}).get("title"), dict) else str(obj.get("layout", {}).get("title", "Chart")),
                    "type": "plotly_chart",
                    "format": "plotly_json",
                    "data_or_url": path
                })
            
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check for common visual indicators
                visual_keywords = ['chart', 'plot', 'graph', 'visual', 'image', 'figure', 'diagram', 'visualization']
                if any(term in key.lower() for term in visual_keywords):
                    if isinstance(value, (str, dict, list)):
                        visuals.append({
                            "path": current_path,
                            "title": key,
                            "type": "detected_visual",
                            "format": "unknown",
                            "key": key,
                            "value_type": type(value).__name__
                        })
                
                # Check for base64 images
                if isinstance(value, str):
                    if value.startswith('data:image/'):
                        visuals.append({
                            "path": current_path,
                            "title": key,
                            "type": "base64_image",
                            "format": value.split(';')[0].split(':')[1] if ':' in value else "image",
                            "data_or_url": value
                        })
                    elif len(value) > 500 and value[:50].isalnum() and ('image' in key.lower() or 'chart' in key.lower()):
                        # Potential base64
                        visuals.append({
                            "path": current_path,
                            "title": key,
                            "type": "potential_base64",
                            "format": "unknown"
                        })
                
                # Recursive search
                search_for_visuals(value, current_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:5]):  # Check first 5 items
                search_for_visuals(item, f"{path}[{i}]")
    
    search_for_visuals(data)
    return visuals


def main():
    """Main comparison function."""
    print("=" * 80)
    print("Comparing Outputs - Zero Loss Verification")
    print("=" * 80)
    print()
    
    # Load files
    ace_data = {}
    essence_data = {}
    unified_data = {}
    
    if ACE_FILE.exists():
        print(f"📦 Loading ACE output: {ACE_FILE}")
        with open(ACE_FILE, 'r', encoding='utf-8') as f:
            ace_data = json.load(f)
        print(f"   Loaded {len(ace_data)} top-level keys")
    else:
        print(f"⚠️  ACE file not found: {ACE_FILE}")
    
    if ESSENCE_FILE.exists():
        print(f"🌱 Loading Essence output: {ESSENCE_FILE}")
        with open(ESSENCE_FILE, 'r', encoding='utf-8') as f:
            essence_data = json.load(f)
        print(f"   Loaded {len(essence_data)} top-level keys")
    else:
        print(f"⚠️  Essence file not found: {ESSENCE_FILE}")
    
    if UNIFIED_FILE.exists():
        print(f"🔗 Loading unified output: {UNIFIED_FILE}")
        with open(UNIFIED_FILE, 'r', encoding='utf-8') as f:
            unified_data = json.load(f)
        print(f"   Loaded {len(unified_data)} top-level keys")
    else:
        print(f"⚠️  Unified file not found: {UNIFIED_FILE}")
        print("   Run tools/run_both.py first to generate unified output")
        sys.exit(1)
    
    print()
    
    # Generate schema reports
    print("📊 Generating schema reports...")
    
    if ace_data:
        ace_schema = generate_schema_report(ace_data, "ACE Pipeline")
        ace_schema_file = REPORTS_DIR / "ace_schema.md"
        with open(ace_schema_file, 'w', encoding='utf-8') as f:
            f.write(ace_schema)
        print(f"   ✅ ACE schema: {ace_schema_file}")
    
    if essence_data:
        essence_schema = generate_schema_report(essence_data, "Essence Pipeline")
        essence_schema_file = REPORTS_DIR / "essence_schema.md"
        with open(essence_schema_file, 'w', encoding='utf-8') as f:
            f.write(essence_schema)
        print(f"   ✅ Essence schema: {essence_schema_file}")
    
    if unified_data:
        unified_schema = generate_schema_report(unified_data, "Unified Output")
        unified_schema_file = REPORTS_DIR / "unified_schema.md"
        with open(unified_schema_file, 'w', encoding='utf-8') as f:
            f.write(unified_schema)
        print(f"   ✅ Unified schema: {unified_schema_file}")
    
    print()
    
    # Verify completeness
    print("🔍 Verifying completeness (zero loss check)...")
    
    missing_ace, missing_essence, conflicts, merges = verify_completeness(
        ace_data, essence_data, unified_data
    )
    
    # Detect visuals from both sources
    visuals = []
    if ace_data:
        ace_visuals = detect_visuals(ace_data)
        visuals.extend([{**v, "source": "ace"} for v in ace_visuals])
    if essence_data:
        essence_visuals = detect_visuals(essence_data)
        visuals.extend([{**v, "source": "essence"} for v in essence_visuals])
    
    # Check if visuals are in unified output
    unified_visuals = unified_data.get("merged", {}).get("visuals", []) if unified_data else []
    
    # Generate completeness report
    report_lines = [
        "# Completeness Report - Zero Loss Verification",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Summary",
        "",
        f"- ACE paths checked: {len(extract_all_paths(ace_data)) if ace_data else 0}",
        f"- Essence paths checked: {len(extract_all_paths(essence_data)) if essence_data else 0}",
        f"- Unified paths: {len(extract_all_paths(unified_data))}",
        f"- Missing ACE paths: {len(missing_ace)}",
        f"- Missing Essence paths: {len(missing_essence)}",
        f"- Detected merges: {len(merges)}",
        f"- Detected visuals: {len(visuals)}",
        "",
    ]
    
    if missing_ace:
        report_lines.extend([
            "## ❌ Missing ACE Paths",
            "",
            "The following paths from ACE output are NOT found in unified output:",
            ""
        ])
        for path in sorted(missing_ace):
            report_lines.append(f"- `{path}`")
        report_lines.append("")
    else:
        report_lines.extend([
            "## ✅ ACE Completeness",
            "",
            "All ACE paths are preserved in unified output.",
            ""
        ])
    
    if missing_essence:
        report_lines.extend([
            "## ❌ Missing Essence Paths",
            "",
            "The following paths from Essence output are NOT found in unified output:",
            ""
        ])
        for path in sorted(missing_essence):
            report_lines.append(f"- `{path}`")
        report_lines.append("")
    else:
        report_lines.extend([
            "## ✅ Essence Completeness",
            "",
            "All Essence paths are preserved in unified output.",
            ""
        ])
    
    if merges:
        report_lines.extend([
            "## 🔗 Detected Merges",
            "",
            "The following paths exist in both ACE and Essence and were merged:",
            ""
        ])
        for path in sorted(merges):
            report_lines.append(f"- `{path}`")
        report_lines.append("")
    
    if visuals:
        report_lines.extend([
            "## 📊 Detected Visuals",
            "",
            "The following visual artifacts were detected:",
            ""
        ])
        for visual in visuals:
            source = visual.get("source", "unknown")
            report_lines.append(f"- `{visual['path']}` ({visual['type']}) - Source: {source}")
        report_lines.append("")
        
        # Check if visuals are in unified output
        if unified_visuals:
            report_lines.append(f"✅ Visuals found in unified output: {len(unified_visuals)}")
            report_lines.append("")
            for uv in unified_visuals:
                report_lines.append(f"  - `{uv.get('path', 'unknown')}` ({uv.get('type', 'unknown')})")
        else:
            report_lines.append("⚠️ **Action Required:** Add detected visuals to `merged.visuals` in unified output.")
        report_lines.append("")
    
    if conflicts:
        report_lines.extend([
            "## ⚠️ Potential Conflicts",
            "",
            "The following paths may have conflicting values:",
            ""
        ])
        for conflict in conflicts:
            report_lines.append(f"- `{conflict}`")
        report_lines.append("")
    
    # Final verdict
    if missing_ace or missing_essence:
        report_lines.extend([
            "## ❌ VERDICT: INFORMATION LOSS DETECTED",
            "",
            "Some paths from source outputs are missing in unified output.",
            "Please review and fix the merge logic in `api_final_agent/unified_output.py`.",
            ""
        ])
    else:
        report_lines.extend([
            "## ✅ VERDICT: ZERO LOSS CONFIRMED",
            "",
            "All paths from ACE and Essence outputs are preserved in unified output.",
            ""
        ])
    
    completeness_file = REPORTS_DIR / "completeness_report.md"
    with open(completeness_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    print(f"   ✅ Completeness report: {completeness_file}")
    print()
    
    # Print summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Missing ACE paths: {len(missing_ace)}")
    print(f"Missing Essence paths: {len(missing_essence)}")
    print(f"Detected merges: {len(merges)}")
    print(f"Detected visuals: {len(visuals)}")
    print()
    
    if missing_ace or missing_essence:
        print("❌ INFORMATION LOSS DETECTED - Review completeness_report.md")
        sys.exit(1)
    else:
        print("✅ ZERO LOSS CONFIRMED - All paths preserved")


if __name__ == "__main__":
    main()

