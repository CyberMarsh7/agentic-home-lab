"""
Voice Interface Service
Routes voice commands from avatar to OpenClaw agents (Hermes, Oracle, Samantha)
Fully accessible: push-to-talk only, no wake words, no always-listening
"""

import subprocess
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os
import sys
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenClawRouter:
    """Routes voice commands to appropriate OpenClaw agent"""

    # Agent endpoints (from agentic-home-lab README)
    AGENTS = {
        'hermes': {
            'role': 'Master orchestrator',
            'location': 'victus',
            'capabilities': ['orchestration', 'scheduling', 'vision', 'reasoning'],
            'command': ['openclaw', 'agent', '--agent', 'hermes', '--message']
        },
        'oracle': {
            'role': 'Visual/creative agent',
            'location': 'pyramid',
            'capabilities': ['vision', 'design', 'creative', 'local-models'],
            'command': ['openclaw', 'agent', '--agent', 'oracle', '--message']
        },
        'samantha': {
            'role': 'Security/local agent',
            'location': 'victus',
            'capabilities': ['security', 'monitoring', 'local-control'],
            'command': ['openclaw', 'agent', '--agent', 'samantha', '--message']
        }
    }

    def __init__(self):
        self.agent_status = {name: 'unknown' for name in self.AGENTS}
        self.last_heartbeat = {name: None for name in self.AGENTS}
        self.message_history = []
        self.refresh_agent_status()

    def refresh_agent_status(self):
        """Check which agents are actually online"""
        logger.info("🔍 Checking agent status...")

        try:
            result = subprocess.run(
                ['bash', os.path.join(os.path.dirname(__file__), '..', 'scripts', 'fleet-status.sh')],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Parse fleet status output
            for agent_name in self.AGENTS:
                if agent_name in result.stdout.lower():
                    # Simplified check - would parse real output
                    self.agent_status[agent_name] = 'online'
                    self.last_heartbeat[agent_name] = datetime.now()
                else:
                    self.agent_status[agent_name] = 'offline'

            logger.info(f"✅ Agent status: {self.agent_status}")
        except Exception as e:
            logger.error(f"❌ Failed to check status: {e}")

    def classify_command(self, text: str) -> Tuple[str, str]:
        """
        Determine which agent should handle this
        Returns: (agent_name, instruction_for_agent)
        """

        text_lower = text.lower()

        # Security/monitoring → Samantha
        if any(word in text_lower for word in ['security', 'monitor', 'check', 'status', 'safe', 'threat']):
            return 'samantha', text

        # Vision/design/creative → Oracle
        if any(word in text_lower for word in ['image', 'design', 'draw', 'picture', 'look', 'see', 'visual']):
            return 'oracle', text

        # Complex reasoning, scheduling, orchestration → Hermes
        if any(word in text_lower for word in ['schedule', 'when', 'automate', 'organize', 'reason', 'think']):
            return 'hermes', text

        # Device control - try Oracle first (Pyramid), fallback to Hermes
        if any(word in text_lower for word in ['device', 'control', 'turn', 'set', 'activate', 'run']):
            return 'oracle', text

        # Default to Hermes (master orchestrator)
        return 'hermes', text

    def send_command(self, agent_name: str, instruction: str) -> Optional[Dict]:
        """
        Send command to an OpenClaw agent via CLI
        Returns: response dict or None on failure
        """

        if agent_name not in self.AGENTS:
            logger.warning(f"❌ Unknown agent: {agent_name}")
            return None

        agent_config = self.AGENTS[agent_name]

        # Build command
        cmd = agent_config['command'] + [instruction]

        logger.info(f"📤 Sending to {agent_name}: {instruction[:100]}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Try to parse JSON response
                try:
                    response = json.loads(result.stdout)
                    logger.info(f"✅ {agent_name} responded")
                    return response
                except json.JSONDecodeError:
                    # Fall back to text response
                    logger.info(f"✅ {agent_name} responded (text)")
                    return {'response': result.stdout, 'agent': agent_name}
            else:
                logger.error(f"❌ {agent_name} error: {result.stderr}")
                return {'error': result.stderr, 'agent': agent_name}

        except subprocess.TimeoutExpired:
            logger.error(f"❌ {agent_name} timeout (>30s)")
            return {'error': 'Agent timeout', 'agent': agent_name}
        except Exception as e:
            logger.error(f"❌ Failed to send to {agent_name}: {e}")
            return {'error': str(e), 'agent': agent_name}

    def process_voice_command(self, text: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a voice command and route to appropriate agent
        """

        logger.info(f"🎤 Voice command: {text}")

        # Store in history
        self.message_history.append({
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        })

        # Classify
        agent_name, instruction = self.classify_command(text)
        logger.info(f"📍 Routing to: {agent_name}")

        # Check if agent is online
        if self.agent_status.get(agent_name) != 'online':
            logger.warning(f"⚠️  {agent_name} may be offline, trying anyway...")

        # Send command
        response = self.send_command(agent_name, instruction)

        # Format response for voice output
        if response:
            if 'response' in response:
                voice_response = response['response']
            elif 'error' in response:
                voice_response = f"Agent error: {response['error']}"
            else:
                voice_response = "Command executed"
        else:
            voice_response = f"Failed to reach {agent_name}"

        return {
            'response': voice_response,
            'agent': agent_name,
            'status': 'success' if response and 'error' not in response else 'failed',
            'timestamp': datetime.now().isoformat()
        }

    def get_system_status(self) -> Dict:
        """Get current system status for UI"""
        self.refresh_agent_status()
        return {
            'agents': self.agent_status,
            'last_heartbeat': self.last_heartbeat,
            'uptime': sum(1 for s in self.agent_status.values() if s == 'online'),
            'total': len(self.AGENTS)
        }

    def get_agent_info(self) -> List[Dict]:
        """Get info about all agents"""
        return [
            {
                'name': name,
                'role': config['role'],
                'location': config['location'],
                'status': self.agent_status.get(name, 'unknown'),
                'capabilities': config['capabilities']
            }
            for name, config in self.AGENTS.items()
        ]


class VoiceInterfaceService:
    """Flask service for voice avatar interface"""

    def __init__(self, router: OpenClawRouter):
        self.router = router
        self.initialization_complete = False

    def process_orchestrate_request(self, request_data: Dict) -> Dict:
        """Process voice command from avatar"""

        request_text = request_data.get('request', '')
        context = request_data.get('context', {})

        if not request_text:
            return {
                'error': 'No request provided',
                'status': 'failed'
            }

        # Process through router
        result = self.router.process_voice_command(request_text, context)

        return {
            'response': result['response'],
            'status': result['status'],
            'agent': result['agent'],
            'timestamp': result['timestamp']
        }

    def get_devices(self) -> Dict:
        """Get device/agent status"""
        status = self.router.get_system_status()
        return {
            'devices': {
                name: {
                    'status': 'online' if status['agents'][name] == 'online' else 'offline',
                    'online': status['agents'][name] == 'online',
                    'role': self.router.AGENTS[name]['role'],
                    'location': self.router.AGENTS[name]['location']
                }
                for name in self.router.AGENTS
            },
            'timestamp': datetime.now().isoformat()
        }

    def get_status(self) -> Dict:
        """Get full system status"""
        return self.router.get_system_status()


# ==================== STANDALONE TEST ====================

def test_voice_interface():
    """Test the voice interface without Flask"""

    logger.info("🎙️  Voice Interface Test")
    logger.info("=" * 50)

    router = OpenClawRouter()

    # Test commands
    test_commands = [
        "What's the security status?",
        "Show me an image of a cat",
        "Schedule a meeting for tomorrow",
        "Turn on the lights",
        "Check system status"
    ]

    for cmd in test_commands:
        logger.info(f"\n📝 Testing: {cmd}")
        result = router.process_voice_command(cmd)
        logger.info(f"✅ Result: {result}")
        time.sleep(1)


if __name__ == '__main__':
    # Test mode
    if '--test' in sys.argv:
        test_voice_interface()
    else:
        # Production: import and use in orchestrator.py
        logger.info("Voice Interface module loaded")
        logger.info("Import OpenClawRouter and VoiceInterfaceService to use")
