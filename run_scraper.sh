#!/usr/bin/env bash
set -e

echo "=== Consider Job Scraper Automation ==="

# 1. Set up a local Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install required packages
echo "[+] Installing required Python libraries..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 4. Run the scraper
echo "[+] Running Airtable Job Scraper..."
python3 job_tracker_Airtable.py

echo "=== Sync Complete! Check your Airtable base. ==="