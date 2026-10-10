"""
Kokoro Expression Recognition
Reads your face. Understands your emotions. Truly knows you.
"""

import logging
from typing import Dict, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ExpressionRecognition:
    """
    Reads facial expressions in real-time.
    Detects: happiness, sadness, anger, surprise, fear, disgust, neutral, confused.
    Remembers patterns. Adapts responses to your emotional state.
    """

    def __init__(self):
        """Initialize expression recognition"""
        self.expression_history = []
        self.current_expression = 'neutral'
        self.confidence = 0.0
        self.patterns = {}
        self.emotional_baseline = 'neutral'

    def process_face_data(self, face_data: Dict) -> Dict:
        """
        Process facial recognition data from browser

        Args:
            face_data: {
                'expressions': {
                    'happy': 0-1,
                    'sad': 0-1,
                    'angry': 0-1,
                    'surprised': 0-1,
                    'fearful': 0-1,
                    'disgusted': 0-1,
                    'neutral': 0-1,
                    'confused': 0-1
                },
                'landmarks': {...},  # eye, nose, mouth positions
                'timestamp': ISO string
            }

        Returns:
            {
                'primary_emotion': str,
                'confidence': float,
                'detected_mood': str,
                'response_hint': str,
                'animation_trigger': str
            }
        """

        expressions = face_data.get('expressions', {})

        if not expressions:
            return {
                'primary_emotion': self.current_expression,
                'confidence': 0.0,
                'detected_mood': 'unclear',
                'response_hint': 'face_not_visible'
            }

        # Find dominant emotion
        primary = max(expressions.items(), key=lambda x: x[1])
        emotion_name = primary[0]
        confidence = primary[1]

        # Store in history
        self.expression_history.append({
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion_name,
            'confidence': confidence,
            'all_expressions': expressions
        })

        if len(self.expression_history) > 500:
            self.expression_history.pop(0)

        self.current_expression = emotion_name
        self.confidence = confidence

        # Detect mood trends
        mood = self._analyze_mood_trend(expressions)

        # Generate response hint for Kokoro
        response_hint = self._get_response_hint(emotion_name, confidence, expressions)

        # Animation trigger
        animation_trigger = self._get_animation_trigger(emotion_name, confidence)

        logger.info(f"Expression detected: {emotion_name} ({confidence:.2f}) - Mood: {mood}")

        return {
            'primary_emotion': emotion_name,
            'confidence': confidence,
            'detected_mood': mood,
            'response_hint': response_hint,
            'animation_trigger': animation_trigger,
            'all_scores': expressions
        }

    def _analyze_mood_trend(self, current_expressions: Dict) -> str:
        """
        Analyze recent expression history to detect mood trends

        Returns: 'happy', 'sad', 'anxious', 'calm', 'excited', 'confused', 'focused', 'neutral'
        """

        if len(self.expression_history) < 3:
            return 'neutral'

        recent = self.expression_history[-10:]

        # Calculate averages
        happy_avg = sum(e['all_expressions'].get('happy', 0) for e in recent) / len(recent)
        sad_avg = sum(e['all_expressions'].get('sad', 0) for e in recent) / len(recent)
        angry_avg = sum(e['all_expressions'].get('angry', 0) for e in recent) / len(recent)
        surprised_avg = sum(e['all_expressions'].get('surprised', 0) for e in recent) / len(recent)
        fearful_avg = sum(e['all_expressions'].get('fearful', 0) for e in recent) / len(recent)
        confused_avg = sum(e['all_expressions'].get('confused', 0) for e in recent) / len(recent)

        # Determine mood
        if happy_avg > 0.6:
            return 'happy'
        elif sad_avg > 0.5:
            return 'sad'
        elif angry_avg > 0.4:
            return 'angry'
        elif fearful_avg > 0.4 or (surprised_avg > 0.5 and fearful_avg > 0.2):
            return 'anxious'
        elif confused_avg > 0.4:
            return 'confused'
        elif surprised_avg > 0.6:
            return 'excited'
        else:
            return 'neutral'

    def _get_response_hint(self, emotion: str, confidence: float, all_expressions: Dict) -> str:
        """
        Generate a hint for Kokoro on how to respond

        This is injected into her response generation
        """

        if confidence < 0.3:
            return 'uncertain_expression'

        hints = {
            'happy': 'user_is_joyful_mirror_energy',
            'sad': 'user_is_sad_be_comforting',
            'angry': 'user_is_frustrated_be_calm_helpful',
            'surprised': 'user_is_surprised_curious_engage',
            'fearful': 'user_is_scared_be_reassuring_protective',
            'disgusted': 'user_is_disapproving_respect_that',
            'neutral': 'user_is_calm_be_steady',
            'confused': 'user_is_confused_be_clear_patient'
        }

        return hints.get(emotion, 'neutral_expression')

    def _get_animation_trigger(self, emotion: str, confidence: float) -> str:
        """
        Get animation trigger for avatar based on expression
        """

        triggers = {
            'happy': 'celebrate_bright_eyes_smile',
            'sad': 'concerned_gentle_slower',
            'angry': 'alert_intense_serious',
            'surprised': 'eyes_wide_head_tilt',
            'fearful': 'defensive_protective_pulse',
            'disgusted': 'recoil_slight_shake',
            'neutral': 'breathing_calm',
            'confused': 'questioning_head_tilt_blink'
        }

        return triggers.get(emotion, 'breathing_calm')

    def get_expression_stats(self) -> Dict:
        """
        Get statistics on expression patterns
        Useful for learning about the user over time
        """

        if not self.expression_history:
            return {
                'total_observations': 0,
                'dominant_emotion': 'unknown',
                'emotional_range': 'unknown',
                'patterns': {}
            }

        emotions = [e['emotion'] for e in self.expression_history]
        emotion_counts = {}

        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        dominant = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else 'unknown'

        # Detect patterns (e.g., gets frustrated with certain topics)
        emotional_range = len(set(emotions))

        return {
            'total_observations': len(self.expression_history),
            'dominant_emotion': dominant,
            'emotion_distribution': emotion_counts,
            'emotional_range': 'varied' if emotional_range > 4 else 'consistent',
            'most_recent': self.expression_history[-1] if self.expression_history else None,
            'average_confidence': sum(e['confidence'] for e in self.expression_history) / len(self.expression_history) if self.expression_history else 0
        }

    def get_javascript_module(self) -> str:
        """
        Get JavaScript module for face-api integration in browser

        Detects faces and sends expression data to Flask backend
        """

        return """
// Kokoro Expression Recognition - Face-API Integration
// Reads your face. Understands your emotions. Knows you truly.

async function initExpressionRecognition() {
    // Load face-api models
    const MODEL_URL = '/models/face-api/';

    try {
        await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
            faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
            faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
        ]);

        console.log('Expression recognition loaded');

        // Start expression detection loop
        startExpressionDetection();
    } catch (e) {
        console.warn('Face-API load failed (camera may not be available)', e);
    }
}

async function startExpressionDetection() {
    const video = document.getElementById('expressionCamera');

    if (!video) {
        console.warn('Camera element not found');
        return;
    }

    // Request camera access
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 320, height: 240 }
        });
        video.srcObject = stream;
    } catch (e) {
        console.warn('Camera access denied', e);
        return;
    }

    // Detection loop
    const detectionLoop = setInterval(async () => {
        if (!video.srcObject) return;

        const detections = await faceapi
            .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
            .withFaceExpressions()
            .withFaceLandmarks();

        if (detections && detections.expressions) {
            // Send to backend
            await fetch('/api/expression', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    expressions: detections.expressions,
                    landmarks: detections.landmarks,
                    timestamp: new Date().toISOString()
                })
            });
        }
    }, 500);  // Check every 500ms
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initExpressionRecognition);
"""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    er = ExpressionRecognition()

    # Simulate happy face
    happy_face = {
        'expressions': {
            'happy': 0.85,
            'sad': 0.02,
            'angry': 0.01,
            'surprised': 0.05,
            'fearful': 0.01,
            'disgusted': 0.01,
            'neutral': 0.05,
            'confused': 0.01
        },
        'timestamp': datetime.now().isoformat()
    }

    result = er.process_face_data(happy_face)
    print(f"Happy face detected: {result}")

    # Get stats
    print("\nExpression stats:")
    print(er.get_expression_stats())
