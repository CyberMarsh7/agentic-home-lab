# OpenClaw Unified System Vision

## The Face
**RasPad is the frame.** A geospatial female face displays on the RasPad screen—no buttons, no UI controls. Just a face you talk to.

## How It Works

### User Interaction (No Buttons)
- User speaks to the face: "Generate an image of a sunset"
- Face listens, responds conversationally
- Face sends the request to the appropriate Claw agent
- Agent executes, returns results
- Face shows the result and speaks a summary

### Two Modes of the Face
1. **Conversationalist Mode (A)**: Talk to her like ChatGPT. She answers questions, has conversations.
2. **System Controller Mode (B)**: Tell her what you want a Claw to do. She routes it and executes.

---

## System Architecture

### Hardware Stack
- **Pyramid** (Orchestrator, 8 CPUs, 1.9GB RAM): OpenClaw gateway, supervisor
- **Victus** (Workhorse, GPU): Heavy compute, model inference
- **Kali** (Security, Linux): Network monitoring, safety checks
- **RasPad** (Face): Display, audio I/O, user interface

### Memory & Models
- **2TB SSD** (attached to Pyramid/Victus): Prebuilt models library
  - Image generation (Stable Diffusion)
  - Text-to-speech
  - RAG models
  - Vision/understanding models
- **Unified Memory Pool**: Pyramid + Victus + Kali share RAM via clustering
  - Allows running larger models than any single device
  - Coach agent validates all requests (prevent injection)

### Specialized Agents (Summoned On Demand)
- **Image Agent**: Image generation, manipulation, vision
- **UX/UI Agent**: Design, layout, visual concepts
- **Voice Agent**: Conversation, TTS, STT
- **RAG Agent**: Knowledge base queries (guarded by Coach)
- **System Agent**: Device control, configuration
- **Coach Agent**: Request validation, safety filtering

---

## Data Flow

```
User speaks to Face on RasPad
        ↓
RasPad captures audio (STT)
        ↓
Speech → Conversationalist OR System Controller logic
        ↓
Coach Agent validates request (prevent injection)
        ↓
Route to appropriate Claw agent
        ↓
Agent executes using clustered memory + 2TB models
        ↓
Results returned to RasPad
        ↓
Face displays result + speaks response (TTS)
```

---

## Clustering Strategy

### Memory Pooling
- Pyramid + Victus + Kali expose RAM to a shared memory backend (Redis/similar)
- 2TB SSD acts as overflow cache
- Coach agent manages access, prevents conflicts

### Model Distribution
- Models prebuilt on 2TB SSD
- Agents load models on demand into the shared pool
- Once done, models unload (free up RAM)
- This allows large models to run despite limited individual device RAM

### Orchestration
- Pyramid gateway routes requests to Victus/Kali as needed
- Victus GPU handles heavy inference
- Kali handles security/monitoring
- RasPad face is the unified interface

---

## Why This Works

1. **No Buttons** = Simpler, more natural interface
2. **Conversational** = User can discover functionality by talking
3. **Pooled Resources** = Can run bigger, better models
4. **Specialized Agents** = Each agent does one thing well
5. **Coach Layer** = Safety and control (no prompt injection)
6. **Persistent** = All saved to GitHub, survives reboots

---

## Current Status
- [ ] Clustering backend (memory pool + model serving)
- [ ] Coach agent (validation layer)
- [ ] RasPad face (geospatial avatar, voice I/O)
- [ ] Specialized agents (image, UX, voice, RAG, system)
- [ ] Model management (2TB SSD library)
- [ ] End-to-end testing
