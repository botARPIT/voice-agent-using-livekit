#!/bin/bash
# Start script for the Real Estate Voice Agent

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ "$1" == "--install" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your LiveKit credentials before running."
    exit 1
fi

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run the agent
echo "Starting Real Estate Voice Agent..."
echo "Mode: ${1:-dev} (use 'start' for production)"
echo ""

if [ "$1" == "start" ]; then
    # Production mode
    python run.py start
else
    # Development mode with auto-reload
    python run.py dev
fi
