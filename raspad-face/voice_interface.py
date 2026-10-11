"""
Voice Interface Service - CORRECTED
Routes voice commands from avatar to Pyramid's OpenClaw gateway
Does NOT try to run agents locally - delegates to Pyramid
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PyramidRouter:
    """Routes voice commands to Pyramid's OpenClaw gateway"""

    def __init__(self):
        # Pyramid gateway endpoints (try local first, then Tailscale)
        self.pyramid_local = "http://192.168.1.227:18789"
        self.pyramid_tailscale = "http://marshinpi:18789"

        self.gateway_url = None
        self.message_history = []

        self.find_pyramid()

    def find_pyramid(self):
        """Find Pyramid gateway - try local first, fallback to Tailscale"""
        logger.info("🔍 Finding Pyramid gateway...")

        # Try local network first (faster, more reliable if at home)
        try:
            response = requests.get(f"{self.pyramid_local}/api", timeout=2)
            if response.status_code < 500:
                self.gateway_url = self.pyramid_local
                logger.info(f"✅ Found Pyramid local: {self.pyramid_local}")
                return
        except:
            logger.debug(f"❌ Local Pyramid unreachable")

        # Fall back to Tailscale
        try:
            response = requests.get(f"{self.pyramid_tailscale}/api", timeout=5)
            if response.status_code < 500:
                self.gateway_url = self.pyramid_tailscale
                logger.info(f"✅ Found Pyramid via Tailscale: {self.pyramid_tailscale}")
                return
        except:
            logger.warning(f"❌ Tailscale Pyramid also unreachable")

        logger.warning("⚠️  Pyramid gateway unreachable - will try again on next request")

    def process_voice_command(self, text: str, context: Optional[Dict] = None) -> Dict:
        """
        Process a voice command by sending to Pyramid's OpenClaw gateway
        Pyramid decides which agent (Hermes/Oracle/Samantha) should handle it
        """

        logger.info(f"🎤 Voice command: {text}")

        if not self.gateway_url:
            self.find_pyramid()

        if not self.gateway_url:
            return {
                'response': "I cannot reach the gateway. Check if Pyramid is online.",
                'status': 'failed',
                'agent': 'none'
            }

        # Store in history
        self.message_history.append({
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        })

        try:
            # Send to Pyramid's OpenClaw gateway
            # The gateway will route to the appropriate agent
            response = requests.post(
                f"{self.gateway_url}/api/orchestrate",
                json={
                    'request': text,
                    'source': 'raspad-avatar',
                    'timestamp': datetime.now().isoformat()
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                agent = data.get('agent', 'unknown')
                voice_response = data.get('response', 'Command processed')

                logger.info(f"✅ {agent} responded: {voice_response[:100]}")

                return {
                    'response': voice_response,
                    'agent': agent,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Gateway returned {response.status_code}")
                return {
                    'response': f"Gateway error: {response.status_code}",
                    'status': 'failed',
                    'agent': 'gateway'
                }

        except requests.exceptions.Timeout:
            logger.error("❌ Gateway timeout (>30s)")
            return {
                'response': "The gateway is taking too long to respond. Try again.",
                'status': 'timeout',
                'agent': 'gateway'
            }
        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to gateway")
            self.gateway_url = None  # Reset to try again next time
            return {
                'response': "Lost connection to gateway. Trying again...",
                'status': 'offline',
                'agent': 'gateway'
            }
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return {
                'response': f"Error: {str(e)}",
                'status': 'error',
                'agent': 'gateway'
            }

    def get_status(self) -> Dict:
        """Get Pyramid gateway status"""
        if not self.gateway_url:
            return {
                'gateway': 'offline',
                'reachable': False,
                'agents': {}
            }

        try:
            response = requests.get(f"{self.gateway_url}/api/health", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass

        return {
            'gateway': 'online',
            'reachable': True,
            'agents': {}
        }


class VoiceInterfaceService:
    """Flask service wrapper for voice avatar"""

    def __init__(self, router: PyramidRouter):
        self.router = router

    def process_orchestrate_request(self, request_data: Dict) -> Dict:
        """Process voice command from avatar"""

        request_text = request_data.get('request', '')
        context = request_data.get('context', {})

        if not request_text:
            return {
                'error': 'No request provided',
                'status': 'failed'
            }

        return self.router.process_voice_command(request_text, context)

    def get_devices(self) -> Dict:
        """Get gateway status (for UI)"""
        status = self.router.get_status()
        return {
            'devices': {
                'pyramid': {
                    'status': 'online' if status.get('reachable') else 'offline',
                    'online': status.get('reachable', False),
                    'role': 'OpenClaw Gateway',
                    'location': 'local + tailscale'
                }
            },
            'timestamp': datetime.now().isoformat()
        }

    def get_status(self) -> Dict:
        """Get full system status"""
        return self.router.get_status()
