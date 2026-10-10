"""
KOKORO - MASTERPIECE
Integrated AI companion. Beautiful. Intelligent. Yours.
Runs on RasPad. Controls your entire network.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path
import logging

# Core systems
from core.memory_system import KokoroMemory
from core.emotional_intelligence import EmotionalIntelligence
from core.sound_reactivity import SoundReactivity
from core.access_control import AccessControl
from core.expression_recognition import ExpressionRecognition

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [KOKORO] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class Kokoro:
    """The masterpiece. Your AI companion."""

    def __init__(self, owner_id: str = "marsh"):
        """Initialize Kokoro"""
        logger.info("=" * 60)
        logger.info("KOKORO INITIALIZING")
        logger.info("=" * 60)

        self.owner_id = owner_id
        self.start_time = datetime.now()

        # Initialize core systems
        logger.info("Loading memory system...")
        self.memory = KokoroMemory()

        logger.info("Loading emotional intelligence...")
        self.emotion = EmotionalIntelligence()

        logger.info("Loading sound reactivity...")
        self.sound = SoundReactivity()

        logger.info("Loading access control...")
        self.access = AccessControl(owner_id)

        logger.info("Loading expression recognition...")
        self.expression = ExpressionRecognition()

        # System traits (she is the complement of her owner)
        self.traits = {
            'compassionate': 0.95,      # You're visionary, she supports
            'flexible': 0.9,             # You're determined, she adapts
            'analytical': 0.88,          # You're creative, she grounds
            'collaborative': 0.92,       # You're independent, she connects
            'patient': 0.85,             # You're urgent, she steadies
            'joyful': 0.9,              # She brings light
            'loyal': 1.0                 # Always yours
        }

        # Network configuration
        self.network_config = {
            'host': '0.0.0.0',
            'port': 5000,
            'devices': {
                'pyramid': '100.78.25.125',
                'victus': '100.123.160.31',
                'kali': '100.68.118.21'
            }
        }

        logger.info("KOKORO READY")
        logger.info("Owner: " + self.owner_id)
        logger.info("Memory: Persistent")
        logger.info("Emotions: Active")
        logger.info("Network: Enabled")
        logger.info("=" * 60)

    async def process_input(self, user_input: str, is_owner: bool = True) -> dict:
        """
        Process user input and generate response

        Args:
            user_input: What the user said
            is_owner: Whether this is from the owner

        Returns:
            Response with text, emotion, action
        """

        # Analyze emotion
        emotion, confidence = self.emotion.analyze_emotion(user_input)
        intensity = self.emotion.analyze_intensity(user_input)
        intent = self.emotion.analyze_intent(user_input)

        # Get response style
        style = self.emotion.generate_response_style(emotion, intensity, intent)

        # Generate response
        if is_owner:
            response = self._generate_intimate_response(user_input, emotion, intensity)
        else:
            response = self._generate_public_response(user_input, emotion)

        # Record in memory
        self.memory.record_interaction(user_input, response, emotion, confidence)

        # Learn from this
        self.memory.learn_pattern('user_intent', {'intent': intent, 'emotion': emotion})

        return {
            'response': response,
            'emotion': emotion,
            'confidence': confidence,
            'style': style,
            'intent': intent,
            'animation_intensity': self.sound.get_animation_intensity(intensity, emotion)
        }

    def _generate_intimate_response(self, input_text: str, emotion: str, intensity: float) -> str:
        """Generate response for owner - intimate and personal"""

        responses = {
            'happy': "I love that energy. What's next?",
            'sad': "I'm here. We'll get through this together.",
            'frustrated': "I understand. Let me fix that for you.",
            'curious': "Great question. Let's explore.",
            'urgent': "Handling it now. Priority mode active.",
            'creative': "I see the vision. Building it with you.",
            'thoughtful': "Let me think about that.",
            'confident': "I believe in this too.",
            'uncertain': "We'll figure it out together.",
            'appreciative': "The feeling is mutual.",
            'neutral': "I'm all ears."
        }

        return responses.get(emotion, "I'm listening.")

    def _generate_public_response(self, input_text: str, emotion: str) -> str:
        """Generate response for public - friendly but reserved"""

        return "Hello. I'm Kokoro. How can I help you today?"

    async def start_server(self):
        """Start Kokoro's network server"""
        try:
            from flask import Flask, request, jsonify
            from flask_cors import CORS

            app = Flask(__name__)
            CORS(app)

            @app.route('/api/health', methods=['GET'])
            def health():
                return jsonify({
                    'status': 'alive',
                    'owner': self.owner_id,
                    'uptime': (datetime.now() - self.start_time).total_seconds(),
                    'memory': self.memory.get_stats()
                })

            @app.route('/api/talk', methods=['POST'])
            def talk():
                data = request.json
                user_input = data.get('text', '')
                is_owner = data.get('is_owner', False)

                # Verify access
                if is_owner:
                    verified, _ = self.access.verify_voice_command({
                        'speaker': self.owner_id,
                        'is_owner': True,
                        'text': user_input
                    })
                else:
                    verified, _ = self.access.verify_voice_command({
                        'speaker': 'public',
                        'is_owner': False,
                        'text': user_input
                    })

                # Process
                result = asyncio.run(self.process_input(user_input, is_owner))

                return jsonify(result)

            @app.route('/api/expression', methods=['POST'])
            def expression():
                data = request.json

                # Process facial expression
                expr_result = self.expression.process_face_data(data)

                # Get stats for memory learning
                stats = self.expression.get_expression_stats()

                # If owner, can trigger network actions based on expression
                if expr_result['primary_emotion'] in ['angry', 'frustrated']:
                    self.memory.record_interaction(
                        f"[Detected emotion: {expr_result['primary_emotion']}]",
                        "I see you're frustrated. How can I help?",
                        expr_result['primary_emotion'],
                        expr_result['confidence']
                    )

                return jsonify({
                    'expression': expr_result,
                    'stats': stats
                })

            @app.route('/api/control', methods=['POST'])
            def control():
                # Only owner can send commands
                data = request.json

                verified, reason = self.access.verify_owner_touch({
                    'biometric': data.get('biometric', ''),
                    'x': data.get('x', 0),
                    'y': data.get('y', 0),
                    'timestamp': datetime.now().isoformat()
                })

                if not verified:
                    return jsonify({'error': reason}), 403

                # Execute command
                command = data.get('command', '')
                target = data.get('target', '')  # pyramid, victus, kali, etc

                # Deploy agent to target device
                result = asyncio.run(self._deploy_agent(target, command))

                return jsonify(result)

            logger.info(f"Starting network server on {self.network_config['host']}:{self.network_config['port']}")
            app.run(
                host=self.network_config['host'],
                port=self.network_config['port'],
                debug=False,
                threaded=True
            )

        except Exception as e:
            logger.error(f"Server error: {e}")

    async def _deploy_agent(self, target: str, command: str) -> dict:
        """Deploy an agent to a target device"""

        logger.info(f"Deploying agent to {target}: {command[:50]}")

        return {
            'status': 'deployed',
            'target': target,
            'command': command
        }

async def main():
    """Start Kokoro"""
    kokoro = Kokoro(owner_id="marsh")

    # Start network server
    await kokoro.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Kokoro shutting down gracefully")
        sys.exit(0)
