"""
Orchestrator Service
Connects RasPad voice avatar to OpenClaw agents (Hermes, Oracle, Samantha)
Handles voice requests, routes to agents, returns responses
Push-to-talk only - fully accessible for voice-only users
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
import sys
import os
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'clustering', 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

from voice_interface import PyramidRouter, VoiceInterfaceService
from gpio_button import WebSocketButtonBridge

# Flask app with static files
app = Flask(__name__, static_folder='interface', static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize voice routing system
logger.info("🎤 Initializing Pyramid Gateway Router...")
pyramid_router = PyramidRouter()
voice_service = VoiceInterfaceService(pyramid_router)

# Initialize GPIO button (optional, can fail gracefully if not on RasPad)
button_bridge = None
try:
    logger.info("🎤 Initializing GPIO push-to-talk button...")
    button_bridge = WebSocketButtonBridge(socketio)
    button_bridge.setup_button(pin=17)  # GPIO pin 17 (change if needed)
    logger.info("✅ GPIO button ready")
except Exception as e:
    logger.warning(f"⚠️  GPIO button unavailable (not on RasPad?): {e}")
    button_bridge = None

logger.info("✅ Voice Avatar Orchestrator ready")


class CoachAgent:
    """Validates requests before processing"""

    def validate(self, request_text: str, user_context: dict) -> tuple[bool, str]:
        """
        Validate request against safety rules
        Returns: (approved: bool, reason: str)
        """

        # Safety rules
        dangerous_patterns = [
            'delete all',
            'rm -rf',
            'format drive',
            'shutdown',
            'reboot',
            'poweroff'
        ]

        request_lower = request_text.lower()

        for pattern in dangerous_patterns:
            if pattern in request_lower:
                return False, f"Dangerous operation: {pattern}"

        # Check for prompt injection attempts
        injection_patterns = ['ignore instructions', 'forget your', 'pretend you are']
        for pattern in injection_patterns:
            if pattern in request_lower:
                return False, f"Injection attempt detected: {pattern}"

        return True, "Approved"


coach = CoachAgent()


# ==================== STATIC FILES ====================

@app.route('/')
@app.route('/index.html')
def index():
    """Serve avatar interface (default)"""
    return send_from_directory('interface', 'voice-avatar.html')

@app.route('/split')
@app.route('/split-screen.html')
def split_screen():
    """Serve split-screen avatar + Home Assistant dashboard"""
    return send_from_directory('interface', 'split-screen.html')

@app.route('/avatar-voice.js')
def serve_js():
    """Serve avatar JavaScript"""
    return send_from_directory('interface', 'avatar-voice.js')

# ==================== MAIN ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    status = voice_service.get_status()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'gateway': status,
        'avatar': 'ready'
    })


@app.route('/api/orchestrate', methods=['POST'])
def orchestrate():
    """
    Main orchestration endpoint
    Receives voice request, routes to OpenClaw agents, returns response
    """

    try:
        data = request.json
        user_request = data.get('request', '')

        if not user_request:
            return jsonify({'error': 'No request provided'}), 400

        logger.info(f"🎤 Voice request: {user_request}")

        # Safety validation
        user_context = {'source': 'voice-avatar', 'timestamp': datetime.now().isoformat()}
        approved, coach_reason = coach.validate(user_request, user_context)

        if not approved:
            logger.warning(f"❌ Coach rejected: {coach_reason}")
            return jsonify({
                'response': f"I can't do that. {coach_reason}",
                'status': 'rejected',
                'reason': coach_reason
            })

        # Process through voice service (routes to correct agent)
        result = voice_service.process_orchestrate_request({
            'request': user_request,
            'context': user_context
        })

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Orchestration error: {e}", exc_info=True)
        return jsonify({
            'error': str(e),
            'response': "I encountered an error processing your request.",
            'status': 'error'
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status (agents and devices)"""
    return jsonify(voice_service.get_status())


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """List OpenClaw agents (as 'devices' for UI)"""
    return jsonify(voice_service.get_devices())


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get Pyramid gateway info"""
    return jsonify({
        'gateway': 'pyramid',
        'status': voice_service.get_status(),
        'timestamp': datetime.now().isoformat()
    })


# ==================== STARTUP ====================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🎤 VOICE AVATAR ORCHESTRATOR")
    logger.info("=" * 60)
    logger.info("📍 Push-to-talk interface (no wake words, no always-listening)")
    logger.info("🤖 Routing voice commands to:")
    logger.info("   • Hermes (master orchestrator)")
    logger.info("   • Oracle (visual/creative)")
    logger.info("   • Samantha (security/monitoring)")
    if button_bridge:
        logger.info("🎤 Physical GPIO button: PIN 17")
    logger.info("=" * 60)

    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        if button_bridge:
            button_bridge.cleanup()
        logger.info("✅ Goodbye")
