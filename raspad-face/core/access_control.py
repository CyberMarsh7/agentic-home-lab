"""
Kokoro Access Control
Only the user can control her. Others can view/speak but can't touch.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AccessControl:
    def __init__(self, owner_id: str):
        """
        Initialize access control

        Args:
            owner_id: unique identifier for the owner (biometric hash, etc)
        """
        self.owner_id = owner_id
        self.touch_events = []
        self.access_log = []
        self.touch_timeout = 30  # seconds of inactivity before resetting
        self.unauthorized_attempts = []

    def verify_owner_touch(self, touch_data: Dict) -> Tuple[bool, str]:
        """
        Verify if touch came from owner

        Args:
            touch_data: {
                'x': int,
                'y': int,
                'pressure': float,
                'timestamp': str,
                'biometric': str (fingerprint hash, etc)
            }

        Returns:
            (is_owner: bool, reason: str)
        """

        biometric = touch_data.get('biometric', '')

        # Check if biometric matches owner
        if self._verify_biometric(biometric):
            self.access_log.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'authorized_touch',
                'user': 'owner',
                'x': touch_data.get('x'),
                'y': touch_data.get('y')
            })
            logger.info("Owner touch verified")
            return True, "Owner verified"

        # Unknown user
        self.unauthorized_attempts.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'unauthorized_touch_attempt',
            'x': touch_data.get('x'),
            'y': touch_data.get('y')
        })

        logger.warning("Unauthorized touch attempt")
        return False, "Only owner can control me"

    def verify_voice_command(self, voice_data: Dict) -> Tuple[bool, str]:
        """
        Verify voice command - less strict than touch

        Anyone can speak to Kokoro, but she responds differently based on owner

        Returns:
            (is_owner: bool, response_type: str)
        """

        speaker = voice_data.get('speaker', 'unknown')

        # Check voice biometric if available
        if speaker == self.owner_id or voice_data.get('is_owner', False):
            response_type = 'owner'
            logger.info("Owner voice detected")
        else:
            response_type = 'public'
            logger.info("Public voice detected")

        self.access_log.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'voice_command',
            'speaker': speaker,
            'response_type': response_type,
            'command': voice_data.get('text', '')[:50]  # Log first 50 chars
        })

        return speaker == self.owner_id, response_type

    def _verify_biometric(self, biometric_hash: str) -> bool:
        """
        Verify biometric against owner's stored biometric

        In production, this would check against secure storage
        """

        if not biometric_hash:
            return False

        # In real implementation, this would:
        # 1. Retrieve stored owner biometric from secure storage
        # 2. Compare with incoming biometric
        # For now, simple hash comparison

        owner_biometric = self._get_owner_biometric()
        return biometric_hash == owner_biometric

    def _get_owner_biometric(self) -> str:
        """
        Get stored owner biometric

        In production: retrieve from secure storage (hardware token, encrypted file, etc)
        """
        # Placeholder - would be loaded from secure storage
        return hashlib.sha256(self.owner_id.encode()).hexdigest()

    def get_response_style(self, is_owner: bool) -> Dict:
        """
        Get response style based on who is speaking

        Owner gets full access and personalized responses
        Public gets read-only, limited responses
        """

        if is_owner:
            return {
                'access_level': 'full',
                'can_touch': True,
                'can_control': True,
                'personality': 'intimate',
                'response_detail': 'full',
                'memory_use': True,
                'agent_deployment': True
            }
        else:
            return {
                'access_level': 'public',
                'can_touch': False,
                'can_control': False,
                'personality': 'friendly',
                'response_detail': 'basic',
                'memory_use': False,
                'agent_deployment': False
            }

    def get_access_report(self) -> Dict:
        """Get access control report"""

        owner_touches = sum(1 for e in self.access_log if e.get('event') == 'authorized_touch')
        public_voices = sum(1 for e in self.access_log if e.get('response_type') == 'public')

        return {
            'owner_id': self.owner_id,
            'owner_touches': owner_touches,
            'public_interactions': public_voices,
            'unauthorized_attempts': len(self.unauthorized_attempts),
            'total_events': len(self.access_log),
            'recent_events': self.access_log[-10:]  # Last 10 events
        }

    def get_javascript_config(self) -> str:
        """
        Get JavaScript configuration for browser

        Embeds access control rules in the client
        """

        return f"""
// Kokoro Access Control
window.KOKORO_ACCESS = {{
    owner_id: "{self.owner_id}",
    can_touch: false,
    is_owner: false,
    access_level: "public"
}};

// Touch handler - check access
document.addEventListener('touchstart', (e) => {{
    if (!window.KOKORO_ACCESS.can_touch) {{
        e.preventDefault();
        console.warn("Only owner can touch Kokoro");
        return false;
    }});
}});

// Voice handler - always allow, response varies
function handleVoiceCommand(text) {{
    const access_level = window.KOKORO_ACCESS.is_owner ? 'owner' : 'public';
    // ... send to orchestrator with access level
}});
"""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Example usage
    ac = AccessControl(owner_id="marsh")

    # Owner touch - should succeed
    owner_touch = {
        'x': 150,
        'y': 250,
        'biometric': hashlib.sha256("marsh".encode()).hexdigest(),
        'timestamp': datetime.now().isoformat()
    }

    is_owner, reason = ac.verify_owner_touch(owner_touch)
    print(f"Owner touch: {is_owner} - {reason}")

    # Unauthorized touch
    unknown_touch = {
        'x': 150,
        'y': 250,
        'biometric': 'unknown_biometric',
        'timestamp': datetime.now().isoformat()
    }

    is_owner, reason = ac.verify_owner_touch(unknown_touch)
    print(f"Unknown touch: {is_owner} - {reason}")

    # Access report
    print("\nAccess Report:")
    print(ac.get_access_report())
