#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"

if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo
echo "=================================================="
echo "  samachar.ai → http://localhost:5000"
echo "=================================================="
echo

python server.py
