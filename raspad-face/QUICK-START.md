# Magic Screen - Quick Start Guide

## 🎤 For Bret (User)

### On a Physical RasPad

```bash
# 1. Clone the code
git clone https://github.com/CyberMarsh7/agentic-home-lab.git
cd agentic-home-lab/raspad-face
git checkout claude/raspi-magic-screen-q37749

# 2. Deploy everything
bash deploy.sh

# This will:
# ✅ Check Python is installed
# ✅ Create virtual environment
# ✅ Install all dependencies
# ✅ Start the Magic Screen server
# ✅ Tell you where to access it
```

### Opening the Interface

Once the server is running, you have **two options**:

#### Option 1: Avatar Only (Simplest)
```
http://localhost:5000/
or
http://<raspad-ip>:5000/
```
- Full-screen animated female avatar
- Press spacebar (or GPIO button) to talk
- Commands go to your OpenClaw agents

#### Option 2: Split-Screen (Avatar + Home)
```
http://localhost:5000/split
or
http://<raspad-ip>:5000/split
```
- Left half: Avatar (voice control)
- Right half: Home Assistant dashboard
- See and control all your home devices in real-time

### Using the Avatar (Both Interfaces)

1. **Press & hold** the pink "Press & Talk" button
   - Or press spacebar on keyboard
   - Or press physical GPIO button (if wired)

2. **Speak your command**
   - "Turn on kitchen light"
   - "What's the weather?"
   - "Run my morning routine"

3. **Avatar responds**
   - Animated mouth, blinking eyes
   - Female voice reads the response
   - Text appears on screen

4. **Release** to stop listening

That's it! 100% voice-controlled.

## 🏠 Setting Up Home Assistant (Optional)

If you have Home Assistant:

1. Get your HA API token (see HA-SETUP.md)
2. Open split-screen: `http://<raspad-ip>:5000/split`
3. Press F12 → Console
4. Paste:
```javascript
localStorage.setItem("ha_url", "http://192.168.1.100:8123")
localStorage.setItem("ha_token", "YOUR_TOKEN_HERE")
location.reload()
```

Then you can say:
- "Turn on kitchen light"
- "What's the temperature?"
- "Lock the front door"

## 🔧 Hardware: GPIO Physical Button (Optional)

To add a real push-to-talk button instead of using spacebar:

1. **Wire a button**:
   - GPIO Pin 17 (Pin 11 on header)
   - Ground (any GND pin)
   - See GPIO-BUTTON-SETUP.md for details

2. **Test it**:
```bash
python gpio-button.py
# Press button a few times, then Ctrl+C
```

3. **It just works** when Magic Screen runs:
```bash
bash deploy.sh
```

## 📱 From Another Device

Can't use the RasPad display? Access from phone/tablet/laptop:

```
http://<raspad-ip>:5000/
or
http://<raspad-ip>:5000/split
```

Same voice interface, works anywhere on your network.

## 🚨 Troubleshooting

### "Can't reach the server"
- Is `bash deploy.sh` still running?
- Is RasPad on the same network?
- Try the IP instead of localhost

### Avatar doesn't respond to voice
- Did you press & hold the button?
- Does your browser have microphone permission?
- Check browser console (F12) for errors

### Home Assistant devices don't show
- Is HA running and accessible?
- Did you configure URL and token correctly?
- Check console log (F12) for error messages

### GPIO button not working
- Did you wire it correctly? (GPIO 17 + GND)
- Does `python gpio-button.py` detect presses?
- Try spacebar instead (always works)

## 📚 Full Documentation

- **README.md** - Overview and features
- **HA-SETUP.md** - Home Assistant configuration
- **GPIO-BUTTON-SETUP.md** - Physical button wiring
- **GPIO-PINOUT.md** - RasPad GPIO reference
- **deploy.sh** - Deployment script

## 🎯 What's Working Now

✅ Avatar interface with Web Speech API  
✅ Voice routing to OpenClaw agents (Pyramid gateway)  
✅ Split-screen with Home Assistant dashboard  
✅ Push-to-talk (spacebar or GPIO button)  
✅ 100% voice-controllable  
✅ No wake words, no always-listening  
✅ Female animated avatar with expressions  

## 🔮 Coming Soon

- Voice commands to configure HA
- Lip-sync animation
- Emotion detection (avatar reacts to context)
- Custom device groups
- Conversation memory
- Multi-language support

---

**That's it.** Press the button, speak, the avatar listens and helps. Everything else is optional.
