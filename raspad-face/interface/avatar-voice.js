/**
 * Voice Avatar Controller
 * Fully voice-driven interface to OpenClaw agents and home devices
 * Push-to-talk for accessibility (no wake words, no always-listening)
 */

class VoiceAvatar {
    constructor() {
        // Browser APIs
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isSpeaking = false;

        // State
        this.currentTask = null;
        this.lastTranscript = '';
        this.messageHistory = [];

        // UI Elements
        this.face = document.getElementById('face');
        this.mouth = document.getElementById('mouth');
        this.transcript = document.getElementById('transcript');
        this.listeningIndicator = document.getElementById('listening-indicator');
        this.talkBtn = document.getElementById('talk-btn');
        this.menuBtn = document.getElementById('menu-btn');

        // Device status
        this.deviceStatus = {
            hermes: { status: 'ready', lastSeen: Date.now() },
            oracle: { status: 'ready', lastSeen: Date.now() },
            samantha: { status: 'ready', lastSeen: Date.now() }
        };

        this.init();
    }

    init() {
        console.log('🎤 Initializing Voice Avatar...');

        // Setup Web Speech API
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            this.showError('Speech Recognition not supported on this device');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false; // Push-to-talk, not continuous
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        // Speech events
        this.recognition.onstart = () => this.onListeningStart();
        this.recognition.onresult = (event) => this.onSpeechResult(event);
        this.recognition.onerror = (event) => this.onListeningError(event);
        this.recognition.onend = () => this.onListeningEnd();

        // Button events
        this.talkBtn.addEventListener('pointerdown', () => this.startListening());
        this.talkBtn.addEventListener('pointerup', () => this.stopListening());
        this.talkBtn.addEventListener('pointercancel', () => this.stopListening());
        this.menuBtn.addEventListener('click', () => this.showMenu());

        // Physical button support (for RasPad GPIO)
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                this.startListening();
            }
        });

        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.stopListening();
            }
        });

        // Setup GPIO WebSocket support
        this.setupGPIOButton();

        // Check device status periodically
        setInterval(() => this.checkDeviceStatus(), 5000);

        // Startup animation
        this.blink();
        this.setMouthState('happy');
        this.showTranscript('Ready to help! Press and hold to talk.', 'default');

        // Voice feedback
        this.speak("Magic screen online. Press and hold the button to talk.");
    }

    // ==================== GPIO BUTTON (WebSocket) ====================

    setupGPIOButton() {
        // Load socket.io client dynamically
        const script = document.createElement('script');
        script.src = 'https://cdn.socket.io/4.5.4/socket.io.min.js';
        script.onload = () => {
            console.log('🎤 GPIO WebSocket support loaded');
            this.connectGPIOSocket();
        };
        script.onerror = () => {
            console.warn('⚠️  Could not load socket.io (GPIO button unavailable)');
        };
        document.head.appendChild(script);
    }

    connectGPIOSocket() {
        if (typeof io === 'undefined') {
            console.warn('⚠️  socket.io not available');
            return;
        }

        const socket = io();

        socket.on('button_press', () => {
            console.log('🎤 GPIO button pressed');
            this.startListening();
        });

        socket.on('button_release', () => {
            console.log('🎤 GPIO button released');
            this.stopListening();
        });

        socket.on('disconnect', () => {
            console.warn('⚠️  GPIO WebSocket disconnected');
        });

        this.gpioSocket = socket;
    }

    // ==================== LISTENING ====================

    startListening() {
        if (this.isListening || this.isSpeaking) return;

        console.log('🎤 Starting to listen...');
        this.isListening = true;
        this.lastTranscript = '';

        // UI feedback
        this.talkBtn.textContent = '🎤 Listening...';
        this.talkBtn.style.opacity = '0.7';
        this.listeningIndicator.classList.add('active');
        this.setMouthState('surprised');
        this.showTranscript('Listening...', 'listening');

        // Start recognition
        try {
            this.recognition.start();
        } catch (e) {
            console.error('Recognition already running');
        }
    }

    stopListening() {
        if (!this.isListening) return;

        console.log('🎤 Stopped listening');
        this.isListening = false;
        this.recognition.stop();
    }

    onListeningStart() {
        console.log('🎤 Recognition started');
    }

    onSpeechResult(event) {
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i].transcript;

            if (event.results[i].isFinal) {
                final += transcript + ' ';
            } else {
                interim += transcript;
            }
        }

        if (final) {
            this.lastTranscript = final.trim();
            console.log('✅ Final:', this.lastTranscript);
            this.showTranscript(`You said: ${this.lastTranscript}`, 'listening');
            this.setMouthState('happy');
        } else if (interim) {
            this.showTranscript(`You said: ${interim}...`, 'listening');
        }
    }

    onListeningError(event) {
        console.error('🔴 Recognition error:', event.error);
        this.showError(`Listening error: ${event.error}`);
        this.setMouthState('thinking');
    }

    onListeningEnd() {
        console.log('🎤 Recognition ended');
        this.talkBtn.textContent = '🎤 Press & Talk';
        this.talkBtn.style.opacity = '1';
        this.listeningIndicator.classList.remove('active');
        this.isListening = false;

        if (this.lastTranscript) {
            this.processVoiceCommand(this.lastTranscript);
        } else {
            this.setMouthState('happy');
        }
    }

    // ==================== VOICE PROCESSING ====================

    processVoiceCommand(text) {
        console.log('📝 Processing:', text);

        this.showTranscript(`Processing: "${text}"...`, 'processing');
        this.setMouthState('thinking');

        // Send to orchestrator
        fetch('/api/orchestrate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request: text,
                source: 'voice-avatar',
                timestamp: new Date().toISOString()
            })
        })
        .then(response => response.json())
        .then(data => this.handleOrchestratorResponse(data, text))
        .catch(err => this.showError(`Processing failed: ${err.message}`));
    }

    handleOrchestratorResponse(data, originalText) {
        const { response, status, task_id, device, model } = data;

        console.log('📦 Response:', response);

        if (status === 'completed' || status === 'pending') {
            this.showTranscript(response, 'response');
            this.setMouthState('happy');

            // Speak the response
            this.speak(response);

            // Store in history
            this.messageHistory.push({
                user: originalText,
                assistant: response,
                device,
                model,
                timestamp: Date.now()
            });
        } else if (status === 'rejected') {
            this.showError(response);
            this.setMouthState('thinking');
            this.speak(response);
        } else {
            this.showError(`Unexpected status: ${status}`);
        }
    }

    // ==================== SPEECH SYNTHESIS ====================

    speak(text) {
        if (this.isSpeaking) {
            this.synthesis.cancel();
        }

        console.log('🔊 Speaking:', text);
        this.isSpeaking = true;
        this.setMouthState('speaking');

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.95; // Slightly slower for clarity
        utterance.pitch = 1.2; // Slightly higher for female voice
        utterance.volume = 1;

        // Select female voice if available
        const voices = this.synthesis.getVoices();
        const femaleVoice = voices.find(v => v.name.includes('female') || v.name.includes('woman'));
        if (femaleVoice) utterance.voice = femaleVoice;

        utterance.onend = () => {
            this.isSpeaking = false;
            this.setMouthState('happy');
            this.blink();
        };

        utterance.onerror = (event) => {
            console.error('🔴 Speech error:', event.error);
            this.isSpeaking = false;
        };

        this.synthesis.speak(utterance);
    }

    // ==================== FACIAL ANIMATIONS ====================

    setMouthState(state) {
        this.mouth.className = 'mouth';
        if (state) this.mouth.classList.add(state);

        console.log(`😀 Mouth: ${state}`);
    }

    blink() {
        this.face.classList.add('blinking');
        setTimeout(() => this.face.classList.remove('blinking'), 400);
    }

    // ==================== DEVICE STATUS ====================

    checkDeviceStatus() {
        fetch('/api/devices')
            .then(response => response.json())
            .then(data => this.updateDeviceStatus(data))
            .catch(err => console.error('Status check failed:', err));
    }

    updateDeviceStatus(data) {
        const devices = data.devices || {};

        // Update status indicators
        for (const [name, device] of Object.entries(devices)) {
            const element = document.getElementById(`${name}-status`);
            if (element) {
                const online = device.online || device.status === 'ready';
                element.className = `status-item ${online ? 'active' : ''}`;
                element.textContent = `${name.toUpperCase()}: ${online ? 'Ready' : 'Offline'}`;
            }
        }
    }

    // ==================== UI ====================

    showTranscript(text, type = 'default') {
        this.transcript.textContent = text;
        this.transcript.className = `transcript ${type}`;
    }

    showError(message) {
        console.error('❌', message);
        this.showTranscript(message, 'error');
        this.setMouthState('thinking');
    }

    showMenu() {
        const menu = `
MAGIC SCREEN MENU
==================

Commands you can say:
• "What devices are online?"
• "Check system status"
• "Run [device/task name]"
• "Stop everything"
• "Show device list"

Or just ask anything - I'll route it to the right agent!

Press OK to close.
        `;

        this.showTranscript(menu, 'response');
        this.speak("Menu opened. You can ask for device status, run tasks, or just talk to me.");
    }
}

// ==================== INITIALIZATION ====================

// Wait for DOM and voices to be ready
document.addEventListener('DOMContentLoaded', () => {
    const avatar = new VoiceAvatar();
    window.avatar = avatar; // Global for debugging
});

// Voices may load async
window.speechSynthesis.onvoiceschanged = () => {
    console.log('✅ Voices loaded:', window.speechSynthesis.getVoices().length);
};
