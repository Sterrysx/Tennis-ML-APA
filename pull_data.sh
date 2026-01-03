#!/bin/bash

# ============================================================================
# ATP Matches Data Download and Merge Pipeline
# ============================================================================
# 
# This script:
# 1. Downloads ATP matches data from Jeff Sackmann's GitHub (2011-2024)
# 2. Merges all years into a single CSV file
# 3. Saves output to: pull-data/parsed_data/atp_matches_2011_2024.csv
#
# Usage:
#   ./pull_data.sh
#
# Requirements:
#   - Python 3.x
#   - pandas, requests (installed via requirements.txt)
# ============================================================================

set -e  # Exit on error

# Get script directory (repo root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "============================================================================"
echo "🎾 ATP Matches Data Pipeline - Starting..."
echo "============================================================================"
echo ""

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p pull-data/atp_matches
mkdir -p pull-data/parsed_data

# Step 1: Download data
echo ""
echo "============================================================================"
echo "📥 Step 1/2: Downloading ATP matches data (2011-2024)..."
echo "============================================================================"
cd pull-data/src
python3 01_download_data.py --start 2011 --end 2024 --outdir ../atp_matches

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Download failed. Please check your internet connection and try again."
    exit 1
fi

# Step 2: Merge data
echo ""
echo "============================================================================"
echo "🔗 Step 2/2: Merging all years into single file..."
echo "============================================================================"
python3 02_merge.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Merge failed. Please check the error messages above."
    exit 1
fi

# Return to repo root
cd "$SCRIPT_DIR"

# Verify output file exists
OUTPUT_FILE="pull-data/parsed_data/atp_matches_2011_2024.csv"
if [ ! -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "❌ Error: Output file not created: $OUTPUT_FILE"
    exit 1
fi

# Summary
echo ""
echo "============================================================================"
echo "✅ Pipeline completed successfully!"
echo "============================================================================"
echo ""
echo "📊 Output file: $OUTPUT_FILE"
echo "📏 File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "📝 Total lines: $(wc -l < "$OUTPUT_FILE" | xargs)"
echo ""
echo "💡 To copy this file to notebooks/data/raw/, run:"
echo "   cp $OUTPUT_FILE notebooks/data/raw/raw_atp_matches.csv"
echo ""
