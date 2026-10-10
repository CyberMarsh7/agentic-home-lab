"""
Kokoro Emotional Intelligence
Analyzes tone, emotion, and context from user input
"""

import re
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class EmotionalIntelligence:
    def __init__(self):
        """Initialize emotional intelligence engine"""

        # Emotion keywords and indicators
        self.emotions = {
            'happy': ['good', 'great', 'love', 'awesome', 'amazing', 'excited', 'wonderful', 'yes', 'perfect'],
            'sad': ['sad', 'down', 'depressed', 'lonely', 'miss', 'hurt', 'pain', 'terrible', 'awful'],
            'frustrated': ['frustrated', 'angry', 'mad', 'annoyed', 'ugh', 'argh', 'dammit', 'stupid', 'broken'],
            'urgent': ['now', 'immediately', 'asap', 'urgent', 'quickly', 'right now', 'emergency', 'critical'],
            'curious': ['how', 'why', 'what', 'tell me', 'explain', 'show me', 'can you', 'interested'],
            'creative': ['imagine', 'create', 'build', 'design', 'dream', 'vision', 'new', 'different', 'unique'],
            'thoughtful': ['think', 'consider', 'maybe', 'perhaps', 'wonder', 'ponder', 'reflect'],
            'confident': ['i know', 'definitely', 'absolutely', 'certainly', 'no doubt', 'for sure'],
            'uncertain': ['not sure', 'maybe', 'i think', 'possibly', 'might', 'could be', 'unsure'],
            'appreciative': ['thanks', 'thank you', 'grateful', 'appreciate', 'nice', 'kind', 'helpful']
        }

        # Tone modifiers
        self.intensity_markers = {
            'exclamation': '!',
            'multiple_exclamation': '!!',
            'caps': '[A-Z]{2,}',
            'elongation': '([a-z])\\1{2,}'
        }

    def analyze_emotion(self, text: str) -> Tuple[str, float]:
        """
        Analyze emotion from text

        Returns:
            (emotion: str, confidence: float 0-1)
        """
        text_lower = text.lower()
        emotion_scores = {}

        # Score each emotion
        for emotion, keywords in self.emotions.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1

            if score > 0:
                emotion_scores[emotion] = score

        if not emotion_scores:
            return 'neutral', 0.5

        # Get dominant emotion
        dominant = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[dominant]
        total_score = sum(emotion_scores.values())

        # Confidence is relative strength
        confidence = max_score / (total_score + 2)  # Normalize
        confidence = min(confidence, 0.99)

        return dominant, confidence

    def analyze_intensity(self, text: str) -> float:
        """
        Analyze intensity/urgency of message

        Returns:
            intensity: float 0-1
        """
        intensity = 0.5  # Start at neutral

        # Exclamation marks
        exclamation_count = text.count('!')
        intensity += (exclamation_count * 0.1)

        # ALL CAPS
        caps_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
        if caps_words > 0:
            intensity += 0.2

        # Repeated letters (HEYYYYY)
        if re.search(r'([a-z])\1{2,}', text.lower()):
            intensity += 0.15

        # Urgent keywords
        urgent_words = ['now', 'immediately', 'asap', 'urgent', 'emergency']
        if any(word in text.lower() for word in urgent_words):
            intensity += 0.25

        return min(intensity, 1.0)

    def analyze_intent(self, text: str) -> str:
        """
        Analyze what the user is trying to accomplish

        Returns:
            intent: 'command', 'question', 'conversation', 'request', 'complaint'
        """
        text_lower = text.lower()

        # Questions
        if text.strip().endswith('?') or text_lower.startswith(('how', 'what', 'why', 'when', 'where', 'who')):
            return 'question'

        # Commands (imperative)
        if text.strip().endswith('!') or any(cmd in text_lower for cmd in ['turn', 'make', 'do', 'get', 'set']):
            return 'command'

        # Complaints
        if any(word in text_lower for word in ['broken', 'not working', 'problem', 'issue', 'frustrated', 'angry']):
            return 'complaint'

        # Requests (polite commands)
        if any(word in text_lower for word in ['can you', 'could you', 'would you', 'please', 'thanks']):
            return 'request'

        # Default to conversation
        return 'conversation'

    def generate_response_style(self, emotion: str, intensity: float, intent: str) -> Dict:
        """
        Generate response style based on emotional analysis

        Returns:
            style dict with tone, speed, emphasis
        """

        styles = {
            'happy': {
                'tone': 'upbeat',
                'emoji_intensity': 0.8,
                'animation_speed': 'fast',
                'response_type': 'enthusiastic'
            },
            'sad': {
                'tone': 'supportive',
                'emoji_intensity': 0.2,
                'animation_speed': 'slow',
                'response_type': 'compassionate'
            },
            'frustrated': {
                'tone': 'solution-focused',
                'emoji_intensity': 0.1,
                'animation_speed': 'medium',
                'response_type': 'action-oriented'
            },
            'curious': {
                'tone': 'educational',
                'emoji_intensity': 0.5,
                'animation_speed': 'medium',
                'response_type': 'informative'
            },
            'urgent': {
                'tone': 'immediate',
                'emoji_intensity': 0.3,
                'animation_speed': 'fast',
                'response_type': 'priority'
            },
            'neutral': {
                'tone': 'balanced',
                'emoji_intensity': 0.4,
                'animation_speed': 'normal',
                'response_type': 'standard'
            }
        }

        style = styles.get(emotion, styles['neutral'])

        # Adjust based on intensity
        if intensity > 0.8:
            style['animation_speed'] = 'fast'
            style['emoji_intensity'] = min(style['emoji_intensity'] + 0.2, 1.0)
        elif intensity < 0.3:
            style['animation_speed'] = 'slow'
            style['emoji_intensity'] = max(style['emoji_intensity'] - 0.2, 0.0)

        return style

    def get_personality_response(self, emotion: str, user_traits: Dict) -> str:
        """
        Generate response that complements user's personality

        Kokoro is the reverse of the user - if they're visionary, she's grounded.
        If they're determined, she's flexible. Etc.
        """

        # Trait reversals
        reversals = {
            'visionary': 'practical',
            'determined': 'flexible',
            'creative': 'analytical',
            'protective': 'open',
            'independent': 'collaborative',
            'serious': 'playful',
            'urgent': 'patient',
            'intense': 'calm'
        }

        # Base responses by emotion
        emotion_responses = {
            'happy': "I'm happy with you. What's next?",
            'sad': "I'm here for you. Let's get through this together.",
            'frustrated': "I understand. Let me fix that for you.",
            'curious': "Great question. Let me explore that with you.",
            'urgent': "Got it. Handling it now.",
            'neutral': "What do you need?"
        }

        return emotion_responses.get(emotion, "I'm listening.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ei = EmotionalIntelligence()

    # Test
    test_inputs = [
        "I'm so happy right now!",
        "I'm frustrated, nothing is working",
        "Can you help me with something?",
        "THIS IS URGENT!!!",
        "What's the meaning of life?"
    ]

    for text in test_inputs:
        emotion, conf = ei.analyze_emotion(text)
        intensity = ei.analyze_intensity(text)
        intent = ei.analyze_intent(text)
        style = ei.generate_response_style(emotion, intensity, intent)

        print(f"\nInput: {text}")
        print(f"Emotion: {emotion} ({conf:.2f})")
        print(f"Intensity: {intensity:.2f}")
        print(f"Intent: {intent}")
        print(f"Style: {style['tone']}")
