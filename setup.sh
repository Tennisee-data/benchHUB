#!/bin/bash
#
# This script prepares the benchHUB application to run on macOS by
# removing the quarantine attribute set by Gatekeeper.

# Get the directory where the script is located to ensure paths are correct.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "--- benchHUB First-Time Setup ---"
echo "Applying permissions to allow the application to run..."

# Define paths to the executables
STARTER_APP="$SCRIPT_DIR/start-benchHUB"
MAIN_APP="$SCRIPT_DIR/benchHUB-macos"

# Remove the quarantine attribute from both executables
# This is necessary because the app is not signed with an Apple Developer ID.
echo "Removing quarantine from the launcher..."
xattr -d com.apple.quarantine "$STARTER_APP" &> /dev/null
echo "Removing quarantine from the main application..."
xattr -d com.apple.quarantine "$MAIN_APP" &> /dev/null

# Also ensure the files are executable, just in case.
chmod +x "$STARTER_APP"
chmod +x "$MAIN_APP"

echo ""
echo "✅ Setup complete!"
echo "The application will now launch."
echo "From now on, you can just double-click 'start-benchHUB' to run it."
echo ""
sleep 2

# Launch the application for the user.
"$STARTER_APP"
