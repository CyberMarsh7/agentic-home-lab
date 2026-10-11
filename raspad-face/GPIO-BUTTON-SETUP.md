# GPIO Physical Push-to-Talk Button Setup

Bret can't use a keyboard spacebar, so the Magic Screen supports a **physical GPIO button** for hands-free push-to-talk control.

## Hardware Required

- **Raspberry Pi RasPad** (already has GPIO pins)
- **Momentary push button** (normally-open, any size)
  - Radio Shack, Adafruit, or similar
  - Cost: $2-5
- **Jumper wires** (male-to-male or male-to-female)
- **Optional: mounting bracket** to attach button to RasPad

## Wiring Diagram

The button connects to:
- **GPIO Pin 17** (BCM numbering)
- **Ground (GND)** pin

```
    RasPad GPIO Header
    ┌─────────────────────┐
    │ ●●●●●●●●●●●●●●●●●● │
    │ ●●●●●●●●●●●●●●●●●● │
    └─────────────────────┘

    GPIO 17 = Pin 11 (6th row, left side)
    GND = Any ground pin (e.g., Pin 6, 9, 14, 20, 25, 30, 34, 39)
```

## Step-by-Step Wiring

### Option A: Soldered Connection (Permanent)

1. Get a 2-pin connector or direct solder connections
2. Connect one wire from **GPIO 17** to one terminal of button
3. Connect other wire from **GND** to other button terminal
4. Mount button to RasPad enclosure or stand

### Option B: Breadboard (Temporary)

1. Place RasPad GPIO ribbon on breadboard
2. Insert one button terminal into GPIO 17 hole
3. Insert other button terminal into GND hole
4. Use jumper wires to extend if needed

### Option C: Pre-Made Button Module

Buy a Raspberry Pi GPIO button module:
- Adafruit: https://www.adafruit.com/search?q=button+module
- Already wired, just plug in

## Testing the Button

After wiring, test that the button works:

```bash
cd /home/user/agentic-home-lab/raspad-face
python gpio-button.py
```

You should see:
```
🎤 GPIO Button initialized on pin 17
✅ GPIO listener started
🎤 Button pressed
🎤 Button released
```

Press the button a few times. Press Ctrl+C to exit test.

## How It Works

1. **Button pressed** → Sends signal to GPIO pin 17 (LOW)
2. **Python detects** → `gpio-button.py` is watching the pin
3. **WebSocket event** → Sends `button_press` to browser
4. **Avatar starts listening** → Web Speech API turns on
5. **Button released** → Sends signal to GPIO pin 17 (HIGH)
6. **Python detects** → Sends `button_release` to browser
7. **Avatar stops listening** → Processes what was said

## Troubleshooting

### Button not detected
```bash
# Check if RPi.GPIO is installed
python3 -c "import RPi.GPIO; print('✅ GPIO support OK')"

# If it fails:
sudo apt install python3-rpi.gpio

# Then test again
python gpio-button.py
```

### Permission denied on GPIO
```bash
# Magic Screen needs GPIO access
# If running as non-root, add user to gpio group:
sudo usermod -aG gpio $USER
# Log out and back in
```

### WebSocket not connecting
- Make sure Magic Screen is running: `bash deploy.sh`
- Check browser console for errors (F12 → Console tab)
- Verify socket.io loaded: look for "GPIO WebSocket support loaded"

## Safety Notes

- **Active-low button**: Button is normally open (not pressed). When pressed, it connects GPIO 17 to GND, pulling the pin LOW.
- **No pull-down resistor needed**: Raspberry Pi GPIO has internal pull-up, so the button alone is enough
- **Debounce**: The code includes 20ms debounce to filter electrical noise

## Physical Button Options

### Best: Arcade Button
- Large, easy to press
- Available on Amazon/eBay (~$5-10)
- Color options (red, yellow, blue, green)
- Looks cool
- Perfect for Bret's accessibility needs

### Good: Tactile Switch
- Small momentary button
- Cheap ($1-2)
- Reliable
- Need to mount on bracket

### Okay: Bell Push Button
- Vintage style
- Loud click feedback (audio confirmation)
- Larger target
- Bit harder to find

## Future Options

Once working, you can also:
- **Add multiple buttons** (one for each agent: Hermes/Oracle/Samantha)
  - Wiredaround different GPIO pins
  - Button 1 (pin 17) = General command
  - Button 2 (pin 27) = Hermes
  - Button 3 (pin 22) = Oracle
  - Button 4 (pin 23) = Samantha
- **Add LED feedback** (lights up when listening)
- **Add haptic feedback** (button vibrates when avatar responds)
- **Voice button activation** (say "start button mode")

## Questions?

If the button isn't working:
1. Run the test: `python gpio-button.py`
2. Check Magic Screen logs: look for "GPIO button ready" or error messages
3. Verify wiring with a multimeter or by running `gpio readall` in terminal

The button should work as soon as you run `bash deploy.sh` and it detects the GPIO pins.
