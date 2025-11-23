#!/bin/bash
# Deploy Slime OS 2 to Pico Calc Hardware
# Automatically detects and uploads all necessary files

set -e  # Exit on error

echo "============================================"
echo "Slime OS 2 - Hardware Deployment Script"
echo "============================================"
echo ""

# Check if mpremote is installed
if ! command -v mpremote &> /dev/null; then
    echo "ERROR: mpremote not found!"
    echo "Install with: pip3 install mpremote"
    exit 1
fi

# Check if device is connected
echo "Checking for connected Pico..."
if ! mpremote connect list &> /dev/null; then
    echo "ERROR: No MicroPython device found!"
    echo "Please connect your Pico via USB"
    exit 1
fi

echo "✓ Pico detected"
echo ""

echo ""
echo "Uploading files..."
echo ""

# Files/directories to exclude from upload
# (dev/ folder contains all development-only files)
EXCLUDE_PATTERNS=(
    "dev"
    "__pycache__"
    "*.pyc"
    ".git"
    "simulator.py"
    "sim_display.py"
    "sim_keyboard.py"
)

# Function to check if a path should be excluded
should_exclude() {
    local path="$1"
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$path" == *"$pattern"* ]]; then
            return 0  # true, should exclude
        fi
    done
    return 1  # false, should not exclude
}

# Function to recursively upload directory
upload_directory() {
    local local_dir="$1"
    local remote_dir="$2"

    # Create remote directory
    if [ -n "$remote_dir" ]; then
        echo "→ Creating directory: $remote_dir"
        mpremote mkdir "$remote_dir" 2>/dev/null || true
    fi

    # Upload files in this directory
    for item in "$local_dir"/*; do
        if [ ! -e "$item" ]; then
            continue  # Skip if doesn't exist
        fi

        local basename=$(basename "$item")
        local remote_path="${remote_dir:+$remote_dir/}$basename"

        # Check if should exclude
        if should_exclude "$item"; then
            continue
        fi

        if [ -f "$item" ]; then
            # It's a file - upload it
            echo "  → $item"
            if [ -n "$remote_dir" ]; then
                mpremote cp "$item" ":$remote_dir/"
            else
                mpremote cp "$item" :
            fi
        elif [ -d "$item" ]; then
            # It's a directory - recurse
            upload_directory "$item" "$remote_path"
        fi
    done
}

# Upload root files (main.py, config.py)
echo "→ Uploading root files..."
for file in main.py config.py; do
    if [ -f "$file" ]; then
        echo "  → $file"
        mpremote cp "$file" :
    fi
done

# Upload lib/ directory
if [ -d "lib" ]; then
    echo ""
    echo "→ Uploading lib/..."
    upload_directory "lib" "lib"
fi

# Upload apps/ directory
if [ -d "apps" ]; then
    echo ""
    echo "→ Uploading apps/..."
    upload_directory "apps" "apps"
fi

# Upload slime/ directory
if [ -d "slime" ]; then
    echo ""
    echo "→ Uploading slime/..."
    upload_directory "slime" "slime"
fi

echo ""
echo "============================================"
echo "✓ Upload complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Reset your Pico (press reset button or unplug/replug)"
echo "2. The launcher should appear on the display"
echo ""
echo "To view serial output:"
echo "  mpremote connect /dev/ttyACM0 repl"
echo ""
echo "To run without reset:"
echo "  mpremote run main.py"
echo ""
