#!/bin/bash

# Flash Atom Echo firmware for Magic Screen
# Make sure Atom Echo is in boot mode (hold button on power-on)

echo "🎤 Flashing Atom Echo Firmware"
echo "=============================="
echo ""
echo "⚠️  Make sure:"
echo "  1. Atom Echo is plugged in via USB"
echo "  2. Atom Echo is in BOOT mode (LED should be dim/red)"
echo ""

# Check if esptool is installed
if ! command -v esptool.py &> /dev/null; then
    echo "📦 Installing esptool..."
    pip install esptool
fi

# Find USB port
PORT=$(ls /dev/ttyUSB* /dev/ttyACM* /dev/cu.* 2>/dev/null | head -1)

if [ -z "$PORT" ]; then
    echo "❌ No USB device found!"
    echo "   Check that Atom Echo is plugged in"
    exit 1
fi

echo "✅ Found device on $PORT"
echo ""

# Compile Arduino code first (requires Arduino IDE)
echo "📝 Note: You need to compile the firmware first using Arduino IDE:"
echo ""
echo "  1. Open Arduino IDE"
echo "  2. Install: M5Atom board (via Board Manager)"
echo "  3. Open: atom-echo-firmware.ino"
echo "  4. Sketch → Export compiled Binary"
echo "  5. This creates: atom-echo-firmware.ino.bin"
echo ""
echo "Then come back and run this again with the .bin file ready"
echo ""

# For now, show the manual process
echo "🔧 Manual Flash (if you have the compiled .bin):"
echo ""
echo "esptool.py -p $PORT -b 921600 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0x1000 atom-echo-firmware.ino.bin"
echo ""
echo "Or use Arduino IDE's built-in flash:"
echo "  1. Tools → Serial Port → $PORT"
echo "  2. Tools → Upload Speed → 921600"
echo "  3. Sketch → Upload"
echo ""

read -p "Press Enter when done flashing..."

echo ""
echo "✅ Firmware flashed!"
echo ""
echo "Next steps:"
echo "  1. Reset Atom Echo (press button)"
echo "  2. It will boot into normal mode"
echo "  3. Edit atom-echo-firmware.ino:"
echo "     - Set WiFi SSID and password"
echo "     - Set RasPad IP address"
echo "  4. Recompile and flash again"
echo ""
