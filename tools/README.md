# Tools for Zero-Loss Verification

This directory contains scripts to verify that the unified output preserves ALL information from ACE and Essence pipelines.

## Scripts

### `run_ace.py`
Runs ACE pipeline and captures raw output.

**Usage:**
```bash
TEST_BARCODE=3017620422003 TEST_OBJECTIVE="Increase flexitarian appeal" python tools/run_ace.py
```

**Output:** `artifacts/ace/ace_raw.json`

### `run_essence.py`
Runs Essence pipeline and captures raw output.

**Usage:**
```bash
TEST_PRODUCT_DESCRIPTION="Plant-based chocolate spread" TEST_OBJECTIVE="Increase market share" python tools/run_essence.py
```

**Output:** `artifacts/essence/essence_raw.json`

### `run_both.py`
Runs both pipelines and generates unified output.

**Usage:**
```bash
TEST_BARCODE=3017620422003 TEST_PRODUCT_DESCRIPTION="Plant-based product" TEST_OBJECTIVE="Comprehensive analysis" python tools/run_both.py
```

**Outputs:**
- `artifacts/ace/ace_raw.json`
- `artifacts/essence/essence_raw.json`
- `artifacts/final/unified.json`

### `compare_outputs.py`
Compares raw outputs with unified output to verify zero information loss.

**Usage:**
```bash
python tools/compare_outputs.py
```

**Prerequisites:** Run `run_both.py` first to generate all outputs.

**Outputs:**
- `artifacts/reports/ace_schema.md` - ACE schema documentation
- `artifacts/reports/essence_schema.md` - Essence schema documentation
- `artifacts/reports/unified_schema.md` - Unified output schema
- `artifacts/reports/completeness_report.md` - Zero-loss verification report

## Workflow

1. **Generate raw outputs:**
   ```bash
   python tools/run_both.py
   ```

2. **Verify completeness:**
   ```bash
   python tools/compare_outputs.py
   ```

3. **Review reports:**
   - Check `artifacts/reports/completeness_report.md`
   - Verify no missing paths
   - Review detected visuals

4. **Fix any issues:**
   - If paths are missing, update `api_final_agent/unified_output.py`
   - If visuals are detected, ensure they're in `merged.visuals`

## Environment Variables

All scripts support these environment variables:

- `TEST_BARCODE` - Product barcode for ACE pipeline
- `TEST_PRODUCT_LINK` - Product URL for Essence pipeline
- `TEST_PRODUCT_DESCRIPTION` - Product description for Essence pipeline
- `TEST_OBJECTIVE` - Business objective (required)
- `TEST_DOMAIN` - Domain filter for Essence (optional)
- `TEST_SEGMENT` - Segment filter for Essence (optional)

## Zero-Loss Verification

The `compare_outputs.py` script performs strict verification:

1. **Extracts all key paths** from ACE, Essence, and unified outputs
2. **Checks completeness**: Every path from ACE/Essence must exist in unified output
3. **Detects conflicts**: Same path with different values
4. **Detects merges**: Paths that exist in both and were merged
5. **Detects visuals**: Charts, plots, images in Essence output

## Expected Results

After running verification:

- ✅ **Zero missing paths** - All information preserved
- ✅ **Visuals detected** - Charts/plots identified and included
- ✅ **Conflicts documented** - Overlapping fields tracked
- ✅ **Merges documented** - Combined fields listed

If any paths are missing, the script exits with code 1 and reports them in `completeness_report.md`.

