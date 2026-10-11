# Atom Echo Push-to-Talk Setup

Use M5Stack Atom Echo as a **wireless push-to-talk remote** for Magic Screen.

## What You Get

- **Portable device**: Hold in hand, press button to talk
- **No screen needed**: Just audio input/output
- **Battery powered**: Works anywhere in WiFi range
- **Voice feedback**: Hear responses through Atom Echo speaker
- **LED status**: Visual feedback (green=ready, blue=listening, yellow=processing)

## Hardware

- M5Stack Atom Echo (2x available - use 1)
- USB cable (for flashing firmware)
- Battery pack or USB power (for operation)
- WiFi connection to RasPad

## Step 1: Prepare Firmware

The firmware file is ready: `atom-echo-firmware.ino`

Before flashing, you need to **edit it with your WiFi details:**

Open `atom-echo-firmware.ino` and find these lines:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* raspad_url = "http://192.168.1.XXX:5000/api/echo-voice";
```

Replace:
- `YOUR_WIFI_SSID` → Your WiFi network name
- `YOUR_WIFI_PASSWORD` → Your WiFi password
- `192.168.1.XXX` → Your RasPad's IP address

## Step 2: Flash Firmware

### Using Arduino IDE (Easiest)

1. **Install Arduino IDE** (if you don't have it)
   - Download from https://www.arduino.cc/en/software

2. **Install M5Atom Board**
   - Arduino IDE → Preferences
   - Additional Board Manager URLs: Add this line:
     ```
     https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/arduino/package_m5stack_index.json
     ```
   - Tools → Board Manager
   - Search "M5Atom"
   - Install "M5Stack by M5Stack Official"

3. **Setup Arduino IDE for Atom Echo**
   - Tools → Board → M5Stack → M5Atom
   - Tools → Port → Select your USB port
   - Tools → Upload Speed → 921600

4. **Prepare Device for Flashing**
   - Plug Atom Echo into USB
   - Hold the **physical button while connecting** to put it in BOOT mode
   - The LED should be red/dim

5. **Flash the Firmware**
   - Open `atom-echo-firmware.ino` in Arduino IDE
   - Click the **Upload button** (right arrow icon)
   - Wait for "Upload complete"

6. **Reset and Test**
   - Unplug USB or press button to reset
   - LED should turn **green** (ready)
   - It should connect to your WiFi
   - Press button → listen for beep

## Step 3: Test Connection

1. **Start Magic Screen on RasPad**
   ```bash
   bash deploy.sh
   ```

2. **Press Atom Echo button**
   - You should hear a **beep** (confirmation)
   - LED turns **blue** (listening)
   - Speak your command

3. **Check Response**
   - RasPad processes command
   - Response comes back through Atom Echo speaker
   - LED turns **green** (ready)

## Step 4: Battery Power

### Option A: USB Battery Pack
- Get any USB power bank
- Plug Atom Echo into power
- It connects to WiFi on startup
- Press button anytime

### Option B: Battery Module
- Buy M5Stack Atom Echo with Base
- Includes rechargeable battery
- Click Atom Echo into base
- Full wireless operation

### Option C: DIY Battery
- Solder wires to USB connector
- Connect to 5V battery pack
- Enclosure for safety

## LED Status Meanings

| Color | Meaning |
|-------|---------|
| 🔴 Red | Booting or error |
| 🟠 Orange | Connecting to WiFi |
| 🟢 Green | Ready (press button) |
| 🔵 Blue | Listening (recording) |
| 🟡 Yellow | Processing (sending to RasPad) |

## Troubleshooting

### Device won't connect to WiFi
- Check SSID and password in firmware
- Recompile and flash again
- Check LED stays green after boot

### Button doesn't respond
- Make sure LED is green
- Press button firmly
- Check Arduino serial monitor for debug output

### No response from RasPad
- Is RasPad running? (`bash deploy.sh` still active)
- Check RasPad IP is correct in firmware
- Check both devices on same WiFi network

### Can't flash firmware
- Put device in BOOT mode (hold button while connecting)
- Try different USB cable
- Check Arduino Board Manager installed M5Atom correctly

## Advanced: Custom Commands

The firmware records when button is pressed and sends to RasPad.

To add custom features, edit `atom-echo-firmware.ino`:
- Double-tap button = different agent
- Hold longer = different mode
- LED patterns for different responses

## Using Multiple Atom Echoes

If you have 2 Atom Echos:
- **Atom Echo 1**: Main push-to-talk
- **Atom Echo 2**: Alarm/notification device
  - Gets real-time updates from RasPad
  - Shows device status
  - Plays alerts

Same firmware works for both (same WiFi credentials).

## Integration with Other Devices

Atom Echo can also trigger:
- **Atom Matrix**: Show animations while listening
- **StackChan**: Animated avatar alongside Atom Echo button
- **Core2/CoreS3**: Full status dashboard while using Echo button

See M5STACK-INTEGRATION.md for details.

## Future Improvements

- [ ] Text-to-speech playback (currently placeholder)
- [ ] Support multiple Atom Echo devices
- [ ] Voice commands to configure WiFi (no USB needed)
- [ ] Custom wake words
- [ ] Conversation history sync with RasPad

## That's It!

You now have a **wireless voice interface** in your hand. Press button, speak, get response. Battery powered, WiFi connected, fully voice-controlled.

No screen. No typing. Just talk.
