# Zero-Loss Verification System

This document describes the complete system for ensuring that the unified output from `API_Final_Agent` preserves **ALL** information from ACE and Essence pipelines.

## Overview

The zero-loss verification system consists of:

1. **Execution Scripts** - Run pipelines and capture raw outputs
2. **Comparison Tool** - Verify completeness and detect missing paths
3. **Schema Reports** - Document all key paths and types
4. **Completeness Report** - Strict verification of information preservation

## Quick Start

### 1. Generate Raw Outputs

Run both pipelines and capture their outputs:

```bash
TEST_BARCODE=3017620422003 \
TEST_PRODUCT_DESCRIPTION="Plant-based chocolate spread" \
TEST_OBJECTIVE="Comprehensive analysis" \
python tools/run_both.py
```

This generates:
- `artifacts/ace/ace_raw.json` - Complete ACE output
- `artifacts/essence/essence_raw.json` - Complete Essence output
- `artifacts/final/unified.json` - Unified merged output

### 2. Verify Completeness

Run the comparison tool:

```bash
python tools/compare_outputs.py
```

This generates:
- `artifacts/reports/ace_schema.md` - ACE schema documentation
- `artifacts/reports/essence_schema.md` - Essence schema documentation
- `artifacts/reports/unified_schema.md` - Unified output schema
- `artifacts/reports/completeness_report.md` - **Zero-loss verification report**

### 3. Review Results

Check `artifacts/reports/completeness_report.md`:

- ✅ **Zero missing paths** - All information preserved
- ✅ **Visuals detected** - Charts/plots identified
- ✅ **Conflicts documented** - Overlapping fields tracked
- ✅ **Merges documented** - Combined fields listed

If any paths are missing, the script exits with code 1.

## Scripts

### `tools/run_ace.py`

Runs ACE pipeline with a barcode and captures raw output.

**Usage:**
```bash
TEST_BARCODE=3017620422003 TEST_OBJECTIVE="Increase flexitarian appeal" python tools/run_ace.py
```

**Output:** `artifacts/ace/ace_raw.json`

### `tools/run_essence.py`

Runs Essence pipeline with product link/description and captures raw output.

**Usage:**
```bash
TEST_PRODUCT_DESCRIPTION="Plant-based product" TEST_OBJECTIVE="Increase market share" python tools/run_essence.py
```

**Output:** `artifacts/essence/essence_raw.json`

### `tools/run_both.py`

Runs both pipelines and generates unified output.

**Usage:**
```bash
TEST_BARCODE=3017620422003 TEST_PRODUCT_DESCRIPTION="Product description" TEST_OBJECTIVE="Analysis" python tools/run_both.py
```

**Outputs:**
- `artifacts/ace/ace_raw.json`
- `artifacts/essence/essence_raw.json`
- `artifacts/final/unified.json`

### `tools/compare_outputs.py`

Compares raw outputs with unified output to verify zero information loss.

**Prerequisites:** Run `run_both.py` first.

**Outputs:**
- Schema reports (Markdown)
- Completeness report (Markdown)
- Exit code 1 if information loss detected

## Verification Process

### Step 1: Extract All Paths

The comparison tool extracts all key paths from:
- ACE raw output
- Essence raw output
- Unified output

Paths use dot notation (e.g., `product_information.basic_info.name`).

### Step 2: Check Completeness

For each path in ACE/Essence outputs:

1. Check if it exists in `raw_sources.ace` or `raw_sources.essence`
2. Check if it exists in `merged` (direct or with prefix)
3. Check if it exists anywhere in unified output

If a path is not found, it's marked as **MISSING**.

### Step 3: Detect Conflicts

Paths that exist in both ACE and Essence with different values are marked as **CONFLICTS**.

### Step 4: Detect Merges

Paths that exist in both ACE and Essence and were merged into `merged` are documented.

### Step 5: Detect Visuals

The tool searches for:
- Plotly chart structures (`data` + `layout` keys)
- Base64 images (`data:image/...`)
- Visual-related keys (`chart`, `plot`, `graph`, `visual`, etc.)

Visuals are checked against `merged.visuals` in unified output.

## Zero-Loss Guarantee

The `unified_output.py` module guarantees zero loss by:

1. **Preserving raw sources**: All ACE and Essence outputs are stored in `raw_sources`
2. **Deep copying**: Using `copy.deepcopy()` to avoid reference issues
3. **Preserving all fields**: Unhandled fields are added with `ace_` or `essence_` prefix
4. **No overwrites**: Conflicts are preserved with source labels
5. **Visual detection**: Automatically detects and includes visual artifacts

## UI Support

The React `ResultsPage` component supports:

1. **Primary rendering**: Displays `merged` data by default
2. **Debug panel**: Collapsible section showing `raw_sources` (ACE + Essence)
3. **Visualizations**: Displays charts/images from `merged.visuals`

### Visual Rendering

- **Base64 images**: Rendered directly as `<img>` tags
- **Plotly charts**: Shows metadata (requires plotly.js for full rendering)
- **Other visuals**: Displays path and type information

## Environment Variables

All scripts support:

- `TEST_BARCODE` - Product barcode for ACE
- `TEST_PRODUCT_LINK` - Product URL for Essence
- `TEST_PRODUCT_DESCRIPTION` - Product description for Essence
- `TEST_OBJECTIVE` - Business objective (required)
- `TEST_DOMAIN` - Domain filter for Essence (optional)
- `TEST_SEGMENT` - Segment filter for Essence (optional)

## Troubleshooting

### Missing Paths Detected

If `compare_outputs.py` reports missing paths:

1. Check `artifacts/reports/completeness_report.md` for details
2. Review `api_final_agent/unified_output.py`
3. Ensure unhandled fields are preserved with prefixes
4. Re-run verification after fixes

### Visuals Not Detected

If visuals exist but aren't detected:

1. Check the visual detection logic in `compare_outputs.py`
2. Verify `unified_output.py` includes visuals in `merged.visuals`
3. Check that visual structures match expected formats

### Script Errors

If scripts fail:

1. Ensure `API_Final_Agent` dependencies are installed
2. Check that pipelines can run independently
3. Verify environment variables are set correctly
4. Review error messages in script output

## Continuous Verification

For CI/CD integration:

```bash
# Run verification and fail on information loss
python tools/run_both.py && python tools/compare_outputs.py
```

Exit code 1 indicates information loss - fix before merging.

## Summary

The zero-loss verification system ensures:

- ✅ All ACE fields preserved
- ✅ All Essence fields preserved
- ✅ Visual artifacts detected and included
- ✅ Conflicts documented (no silent overwrites)
- ✅ Merges tracked and verified
- ✅ UI supports all output types

This guarantees that the unified output is **complete** and **traceable** back to source pipelines.

