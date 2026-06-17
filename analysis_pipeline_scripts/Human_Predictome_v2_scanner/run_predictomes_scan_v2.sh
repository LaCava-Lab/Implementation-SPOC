#!/usr/bin/env bash
set -euo pipefail

#Before running: conda activate predictomes

# Configurable parameters
DATA_PATH="/mnt/storage/ana01/data/elife-30094-supp1-v6_clean_exploded.xlsx" # Input Excel file path with dataset proteins of interest for all-by-all binary interactions scan
SHEET_NAME="Sheet1" # Sheet name in the Excel file to use

PREDICTOMES_CSV="/mnt/storage/ana01/20251110_final_hs_predictome_pairs.csv"
OUT_DIR="/mnt/storage/ana01/results/coIPMS_analysis_pipeline_results_RNase_final"

# Run header
echo "________Predictomes pipeline run (v2)________"
echo "Input Excel file:        $DATA_PATH"
echo "Sheet name:              $SHEET_NAME"
echo "Predictomes CSV:         $PREDICTOMES_CSV"
echo "Output directory:        $OUT_DIR"
echo "Run started at:          $(date)"
echo

# Run predictomes scanner
python3 pipeline_predictomes_scanner_v2.py \
    --data "$DATA_PATH" \
    --sheet_name "$SHEET_NAME" \
    --predictomes_csv "$PREDICTOMES_CSV" \
    --out_dir "$OUT_DIR"

