#!/bin/bash
# batch_scrape.sh - Process multiple pages of Brackeys-13 jam entries

# Configuration
START_PAGE=2
END_PAGE=5
OUTPUT_FILE="brackeys_3d_games_master.csv"
DELAY_BETWEEN_PAGES=3  # seconds

echo "================================================"
echo "Brackeys-13 Batch Scraper"
echo "================================================"
echo "Pages: $START_PAGE to $END_PAGE"
echo "Output: $OUTPUT_FILE"
echo "Delay between pages: ${DELAY_BETWEEN_PAGES}s"
echo "================================================"
echo ""

# Check if Python script exists
if [ ! -f "brackeys_scraper.py" ]; then
    echo "Error: brackeys_scraper.py not found!"
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
python3 -c "import requests, bs4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Required Python packages not installed!"
    echo "Run: pip install -r requirements.txt"
    exit 1
fi
echo "✓ Dependencies OK"
echo ""

# Process first page (creates new file)
echo "Starting batch scrape..."
echo "------------------------"
python3 brackeys_scraper.py --page $START_PAGE --output "$OUTPUT_FILE"

if [ $? -ne 0 ]; then
    echo "Error processing page $START_PAGE. Aborting."
    exit 1
fi

# Process remaining pages (append mode)
for page in $(seq $((START_PAGE + 1)) $END_PAGE)
do
    echo ""
    echo "Waiting ${DELAY_BETWEEN_PAGES}s before next page..."
    sleep $DELAY_BETWEEN_PAGES
    
    echo "------------------------"
    python3 brackeys_scraper.py --page $page --output "$OUTPUT_FILE" --append
    
    if [ $? -ne 0 ]; then
        echo "Warning: Error processing page $page. Continuing..."
    fi
done

echo ""
echo "================================================"
echo "Batch scraping complete!"
echo "================================================"
echo "Results saved to: $OUTPUT_FILE"
echo ""

# Show summary
if [ -f "$OUTPUT_FILE" ]; then
    line_count=$(wc -l < "$OUTPUT_FILE")
    entry_count=$((line_count - 1))  # Subtract header
    echo "Total entries: $entry_count"
    echo ""
    echo "First few entries:"
    head -n 5 "$OUTPUT_FILE"
fi
