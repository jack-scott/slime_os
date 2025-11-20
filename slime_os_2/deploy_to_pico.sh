#!/bin/bash
# Deploy Slime OS 2 to Pico Calc Hardware

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

# Confirm deployment
echo "This will upload Slime OS 2 to your Pico Calc."
echo "Make sure config.py is set to DEVICE = \"pico_calc\""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "Uploading files..."
echo ""

# Upload main files
echo "→ Uploading main.py..."
mpremote cp main.py :

echo "→ Uploading config.py..."
mpremote cp config.py :

# Upload lib/
echo "→ Creating lib/ directory..."
mpremote mkdir lib 2>/dev/null || true
echo "→ Uploading lib/keycode.py..."
mpremote cp lib/keycode.py :lib/

# Upload apps/
echo "→ Creating apps/ directory..."
mpremote mkdir apps 2>/dev/null || true
echo "→ Uploading apps..."
mpremote cp apps/__init__.py :apps/
mpremote cp apps/launcher.py :apps/
mpremote cp apps/flashlight.py :apps/
mpremote cp apps/log_viewer.py :apps/

# Upload slime/ (excluding simulator files)
echo "→ Creating slime/ directory structure..."
mpremote mkdir slime 2>/dev/null || true
mpremote mkdir slime/devices 2>/dev/null || true
mpremote mkdir slime/drivers 2>/dev/null || true
mpremote mkdir slime/drivers/display 2>/dev/null || true
mpremote mkdir slime/drivers/input 2>/dev/null || true

echo "→ Uploading slime core..."
mpremote cp slime/__init__.py :slime/
mpremote cp slime/system.py :slime/
mpremote cp slime/app.py :slime/
mpremote cp slime/logger.py :slime/

echo "→ Uploading slime/devices..."
mpremote cp slime/devices/__init__.py :slime/devices/
mpremote cp slime/devices/base.py :slime/devices/
mpremote cp slime/devices/pico_calc.py :slime/devices/

echo "→ Uploading slime/drivers..."
mpremote cp slime/drivers/__init__.py :slime/drivers/

echo "→ Uploading slime/drivers/display..."
mpremote cp slime/drivers/display/__init__.py :slime/drivers/display/
mpremote cp slime/drivers/display/abstract.py :slime/drivers/display/
mpremote cp slime/drivers/display/pico_calc_display.py :slime/drivers/display/

echo "→ Uploading slime/drivers/input..."
mpremote cp slime/drivers/input/__init__.py :slime/drivers/input/
mpremote cp slime/drivers/input/abstract.py :slime/drivers/input/
mpremote cp slime/drivers/input/pico_calc_keyboard.py :slime/drivers/input/

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
