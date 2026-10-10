# Pee-wee's Magic Screen for Accessibility

A fullscreen voice-driven avatar interface for Raspberry Pi that gives you access to all your OpenClaw smart home agents. **Push-to-talk only** — no wake words, no always-listening. Designed for people who can't type or click precisely.

## What It Is

A female avatar face that you talk to. She listens via microphone, routes your commands to your smart home agents (Hermes, Oracle, Samantha), and speaks the responses. Everything happens in the background — the avatar is your interface.

**Perfect for:**
- Voice-only control of your entire home lab
- Accessibility (mobility disabilities, speech recognition preferred)
- Fun, engaging visual feedback while you talk
- No typing, no clicking, 100% verbal

## Hardware

- **Raspberry Pi** with RasPad or touch display
- **Microphone** (USB or 3.5mm)
- **Speakers** (USB or 3.5mm)
- Network access to OpenClaw gateway (Pyramid)

## Quick Start

### 1. Install dependencies

```bash
cd /home/user/agentic-home-lab/raspad-face
pip install -r requirements.txt
```

### 2. Start the orchestrator

```bash
python orchestrator.py
```

This starts the Flask service on port 5000. It will try to connect to your OpenClaw agents on startup.

### 3. Open the avatar interface

In a web browser (or fullscreen on RasPad):

```
http://localhost:5000/interface/voice-avatar.html
```

Or serve it with a web server:

```bash
cd interface
python -m http.server 8000
# Then visit http://localhost:8000/voice-avatar.html
```

## Using It

1. **Press and hold** the big pink "Press & Talk" button
2. **Speak your command** clearly
3. **Release** the button
4. The avatar listens, processes, and **speaks the response**

### Example Commands

- "What devices are online?"
- "Take a screenshot"
- "Check security status"
- "Run device cleanup"
- "What's the system status?"
- Just ask anything — it routes to the right agent

## How It Routes Commands

The voice system automatically sends commands to the right agent:

- **Security/monitoring** → Samantha
- **Visual/creative** → Oracle
- **Scheduling/reasoning** → Hermes
- **Device control** → Oracle (fallback to Hermes)

If in doubt, everything goes to **Hermes** (master orchestrator).

## Architecture

```
┌─────────────────────────────────────────┐
│   voice-avatar.html (fullscreen)        │
│   - Face animation                      │
│   - Web Speech API (browser speech)     │
│   - Microphone input (push-to-talk)     │
│   - Speaker output (TTS)                │
└──────────────┬──────────────────────────┘
               │ (HTTP + JSON)
┌──────────────▼──────────────────────────┐
│   orchestrator.py (Flask service)       │
│   - /api/orchestrate → routes voice     │
│   - /api/devices → agent status         │
│   - /api/agents → detailed info         │
└──────────────┬──────────────────────────┘
               │ (OpenClaw CLI)
┌──────────────▼──────────────────────────┐
│   OpenClaw Agents                       │
│   - Hermes (Victus)                     │
│   - Oracle (Pyramid)                    │
│   - Samantha (Victus)                   │
└─────────────────────────────────────────┘
```

## Accessibility Features

✅ **Push-to-talk only** — no wake words  
✅ **No always-listening** — full privacy, no false triggers  
✅ **Fully verbal** — no typing required  
✅ **Large touch targets** — 200px button (whole lower screen)  
✅ **Voice feedback** — speaks responses out loud  
✅ **High contrast mode** — prefers-contrast media query  
✅ **Customizable** — adjust speech rate, pitch, language  

## Configuration

### Change Voice

In `avatar-voice.js`, modify the `speak()` function:

```javascript
utterance.rate = 0.95;      // Speech speed (0.1-10)
utterance.pitch = 1.2;      // Pitch (0-2, 1 is normal)
utterance.volume = 1;       // Volume (0-1)
```

Or select a specific voice:

```javascript
const voices = this.synthesis.getVoices();
const voice = voices.find(v => v.name === 'Your Voice Name');
utterance.voice = voice;
```

### Change Button Behavior

The button works with:
- **Mouse/touch:** Click and hold
- **Spacebar:** Press and hold (physical button on RasPad)
- **GPIO button:** Wire to GPIO and trigger spacebar via `gpiozero`

### Customize Avatar

Edit `voice-avatar.html` to change:
- Face shape/colors (`.face`, `.blush`, etc.)
- Expression animations (breathing, blinking)
- Button layout
- Status bar information

## Troubleshooting

### No Speech Input

```bash
# Check if browser has microphone permission
# Try Firefox or Chrome (better speech API support)
# Test: https://www.google.com/intl/en/chrome/demos/speech.html
```

### Avatar Not Responding

```bash
# Check orchestrator is running
ps aux | grep orchestrator.py

# Check Flask is listening
netstat -tlnp | grep 5000

# Check agent status
python voice_interface.py --test
```

### Agents Offline

```bash
# Check OpenClaw agents on Victus/Pyramid
ssh marshinpyramid
/usr/bin/openclaw agent --list

# Or run fleet status
bash scripts/fleet-status.sh
```

### Speech Recognition Errors

1. Microphone volume too low — increase input
2. Ambient noise — try quieter environment
3. Accent/dialect — slow down, speak clearly
4. Language mismatch — change `recognition.lang` in JS

## Files

- `voice-avatar.html` — Fullscreen avatar interface
- `avatar-voice.js` — Speech recognition, animations, UI
- `orchestrator.py` — Flask service, routes to OpenClaw
- `voice_interface.py` — OpenClaw agent routing logic

## Next Steps

- [ ] GPIO button support (physical push-to-talk on RasPad)
- [ ] Lip sync animation (animate mouth to speech)
- [ ] Emotion detection (face reacts to context)
- [ ] Device status on avatar (blinking lights)
- [ ] Custom wake phrases (for individual devices)
- [ ] Log conversation history

## License

Part of the agentic-home-lab project. Built for accessibility.
