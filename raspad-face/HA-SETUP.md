# Home Assistant Integration with Magic Screen

The Magic Screen includes a **split-screen dashboard** that shows your Home Assistant devices in real-time and lets you control them via voice.

## What You Get

- **Left half**: Animated avatar for voice commands
- **Right half**: Live Home Assistant dashboard showing all devices
- **Voice control**: "Turn on living room light" → Does it automatically
- **Real-time updates**: Dashboard refreshes every 5 seconds
- **Click to toggle**: You can also tap device tiles to control them

## Prerequisites

1. **Home Assistant running** somewhere accessible from RasPad
   - Can be on the same network or via Tailscale
2. **Home Assistant API token** (created in HA settings)

## Step 1: Get Your Home Assistant API Token

In Home Assistant:
1. Click your profile icon (bottom left)
2. Scroll down to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Give it a name like "Magic Screen"
5. **Copy the token** (you'll need it)

## Step 2: Configure Magic Screen to Connect to HA

When you open the split-screen interface, it checks `localStorage` for your HA settings.

### Option A: Configure via Browser Console (Easiest)

1. Open the split-screen: `http://<raspad-ip>:5000/split`
2. Press F12 to open Developer Tools
3. Click "Console" tab
4. Paste these commands (replace values):

```javascript
localStorage.setItem("ha_url", "http://192.168.1.100:8123")
localStorage.setItem("ha_token", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
location.reload()
```

Replace:
- `192.168.1.100` with your Home Assistant IP
- `8123` with your HA port (usually 8123)
- `eyJhbGc...` with your actual token

### Option B: Configure via Voice (100% Accessible)

Once Avatar is running, say:
> "Configure Home Assistant"

The avatar will guide you through:
1. What's your Home Assistant IP address?
2. What's the port? (usually 8123)
3. Paste your API token

*(This feature will be added in the next update)*

## Step 3: Test the Connection

1. Open split-screen: `http://<raspad-ip>:5000/split`
2. Check browser console (F12 → Console)
3. You should see: `✅ HA configured, fetching entities...`
4. Wait 2-3 seconds
5. Your devices should appear on the right side

### If it doesn't work:

**Check the console for errors:**
- "❌ HA API error: 401" → Bad token
- "❌ HA API error: 404" → Wrong URL/port
- "❌ Failed to fetch HA entities" → Network unreachable

**Test connectivity manually:**
```bash
# From RasPad terminal:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.1.100:8123/api/states | head -20
```

## Voice Commands for Home Assistant

Once configured, you can say:

### Lights
- "Turn on kitchen light"
- "Turn off bedroom lights"
- "Dim the living room to 50 percent"

### Switches & Outlets
- "Turn on the fan"
- "Turn off the coffee maker"

### Locks
- "Lock the front door"
- "Unlock the garage"

### Climate
- "Set temperature to 72 degrees"
- "Turn on the thermostat"

### General
- "Turn on the patio lights"
- "What devices do we have?"
- "Show me the status"

## Using the Split-Screen Interface

### Avatar Side (Left)
- **Press & Hold**: Start listening
- **Speak your command**: "Turn on kitchen light"
- **Avatar responds**: Animated face, TTS voice

### Dashboard Side (Right)
- **Real-time status**: Shows if devices are on/off
- **Click to toggle**: Tap any device to turn on/off
- **Auto-refresh**: Updates every 5 seconds
- **Color coded**: Green = ON, Red = OFF

## Organizing Your Devices

Home Assistant automatically groups devices by type:

| Icon | Category | What Shows Up |
|------|----------|---------------|
| 💡 | Lights | All `light.*` entities |
| 🌡️ | Climate | Thermostats, temp sensors |
| ⚡ | Switches | Plugs, outlet controls |
| 🔐 | Locks | Door locks, garage |
| 📷 | Cameras | Security cameras |
| 📡 | Other | Everything else |

To control devices, they must be added to Home Assistant first.

## Adding New Devices to Home Assistant

This depends on your device type, but generally:

1. **Smart Lights**: Add via Zigbee, WiFi, or Hue Bridge
2. **Switches**: Add via Smart Home integration
3. **Thermostats**: Add via HVAC integration
4. **Locks**: Add via Z-Wave or WiFi
5. **Cameras**: Add via RTSP or integration

See [Home Assistant Docs](https://www.home-assistant.io/docs/configuration/) for specific device setup.

## Troubleshooting

### Dashboard shows "No devices available"
- ✅ HA is connected but you don't have entities yet
- Add some devices to Home Assistant first

### Devices show but controls don't work
- Check HA permissions on the token
- Token might need "read-write" instead of "read-only"

### "HA not configured yet" message
- Open browser console (F12)
- Run the `localStorage.setItem()` commands above
- Check that URL and token are correct

### WebSocket error in console
- This is normal if socket.io isn't loading
- GPIO button still works (spacebar or physical button)
- HA dashboard still works

## Advanced: Using HTTPS

If your HA uses HTTPS:
```javascript
localStorage.setItem("ha_url", "https://192.168.1.100:8123")
```

If you get SSL errors, your self-signed certificate might not be trusted. This is a browser security issue, not a Magic Screen issue.

## Advanced: Remote Access via Tailscale

If you're using Tailscale to access HA remotely:

```javascript
localStorage.setItem("ha_url", "http://victus:8123")  // Tailscale hostname
```

## Questions?

The split-screen is smart and will tell you what's wrong:
- Open browser console (F12 → Console)
- Look for 🏠, ✅, ❌, or ⚠️ messages
- Follow the instructions in the log

That's it! Now you have full voice control of your home + a status dashboard on the same interface.
