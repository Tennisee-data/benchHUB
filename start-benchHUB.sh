#!/bin/bash
# benchHUB Launcher Script for macOS
# This script launches the Python launcher which then starts the main application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python launcher exists
LAUNCHER_PATH="$SCRIPT_DIR/launcher.py"
if [ ! -f "$LAUNCHER_PATH" ]; then
    echo "Error: launcher.py not found in $SCRIPT_DIR"
    echo "Please ensure all files are properly extracted."
    exit 1
fi

# Check if main executable exists
MAIN_APP="$SCRIPT_DIR/benchHUB-macos"
if [ ! -f "$MAIN_APP" ]; then
    echo "Error: benchHUB-macos executable not found in $SCRIPT_DIR"
    echo "Please ensure all files are properly extracted."
    exit 1
fi

# Launch the Python launcher
python3 "$LAUNCHER_PATH"