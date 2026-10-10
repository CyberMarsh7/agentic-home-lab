"""
Kokoro Sound Reactivity
Reacts to sounds and movements in the environment
"""

import numpy as np
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)

class SoundReactivity:
    def __init__(self):
        """Initialize sound reactivity engine"""
        self.last_sound_level = 0
        self.sound_history = []
        self.reaction_threshold = 0.3

    def analyze_audio_level(self, audio_data: np.ndarray) -> Tuple[float, str]:
        """
        Analyze audio level and intensity

        Args:
            audio_data: numpy array of audio samples

        Returns:
            (level: 0-1, intensity_type: 'quiet', 'normal', 'loud', 'very_loud')
        """

        if len(audio_data) == 0:
            return 0.0, 'quiet'

        # Calculate RMS (root mean square)
        rms = np.sqrt(np.mean(audio_data**2))

        # Normalize to 0-1
        level = min(rms / 32768.0, 1.0)  # Assuming 16-bit audio

        # Categorize
        if level < 0.1:
            intensity = 'quiet'
        elif level < 0.3:
            intensity = 'normal'
        elif level < 0.6:
            intensity = 'loud'
        else:
            intensity = 'very_loud'

        self.sound_history.append(level)
        if len(self.sound_history) > 100:
            self.sound_history.pop(0)

        return level, intensity

    def detect_sudden_sound(self) -> bool:
        """Detect sudden loud sound (clapping, etc)"""
        if len(self.sound_history) < 5:
            return False

        recent_avg = np.mean(self.sound_history[-5:])
        previous_avg = np.mean(self.sound_history[-20:-5]) if len(self.sound_history) > 20 else np.mean(self.sound_history[:-5])

        # Sudden spike = recent is significantly louder
        return recent_avg > (previous_avg * 1.5)

    def detect_rhythm(self) -> Tuple[bool, float]:
        """
        Detect rhythmic sounds (music, tapping, etc)

        Returns:
            (has_rhythm: bool, bpm_estimate: float)
        """

        if len(self.sound_history) < 40:
            return False, 0.0

        # Simple rhythm detection via variance
        recent = np.array(self.sound_history[-40:])
        variance = np.std(recent)

        has_rhythm = variance > 0.1

        # Very rough BPM estimation from frequency
        bpm = 60 + (variance * 100)  # 60-160 BPM range

        return has_rhythm, bpm

    def get_animation_intensity(self, sound_level: float, emotion: str = 'neutral') -> float:
        """
        Get animation intensity based on sound and emotion

        Returns:
            intensity: 0-1 for how animated Kokoro should be
        """

        # Base on sound level
        intensity = sound_level * 0.7

        # Boost for emotions
        emotion_boosts = {
            'happy': 0.3,
            'excited': 0.4,
            'frustrated': 0.2,
            'curious': 0.15,
            'urgent': 0.3,
            'neutral': 0.1,
            'sad': -0.2,
            'calm': -0.15
        }

        intensity += emotion_boosts.get(emotion, 0)

        return max(0, min(1.0, intensity))

    def get_movement_direction(self, audio_channels: List[np.ndarray]) -> Tuple[float, float]:
        """
        Estimate direction of sound source (if stereo)

        Args:
            audio_channels: list of audio arrays [left, right, etc]

        Returns:
            (x: -1 to 1, y: -1 to 1) direction vector
        """

        if len(audio_channels) < 2:
            return 0.0, 0.0

        left_level = np.sqrt(np.mean(audio_channels[0]**2))
        right_level = np.sqrt(np.mean(audio_channels[1]**2))

        # Pan left/right
        x_direction = (right_level - left_level) / (left_level + right_level + 0.001)

        # Y can be estimated from frequency analysis
        # For now, random variation
        y_direction = np.random.randn() * 0.3

        return np.clip(x_direction, -1, 1), np.clip(y_direction, -1, 1)

    def get_reaction_animation(self, sound_level: float, intensity_type: str) -> dict:
        """
        Get animation parameters for this sound moment

        Returns:
            dict with animation properties
        """

        animations = {
            'quiet': {
                'head_tilt': 5,
                'eye_movement': 'slow_scan',
                'arm_movement': 'rest',
                'body_sway': 0.5,
                'glow_intensity': 0.3
            },
            'normal': {
                'head_tilt': 10,
                'eye_movement': 'attentive',
                'arm_movement': 'gentle_wave',
                'body_sway': 1.0,
                'glow_intensity': 0.6
            },
            'loud': {
                'head_tilt': 20,
                'eye_movement': 'alert',
                'arm_movement': 'expressive',
                'body_sway': 1.5,
                'glow_intensity': 0.8
            },
            'very_loud': {
                'head_tilt': 30,
                'eye_movement': 'focused',
                'arm_movement': 'dynamic',
                'body_sway': 2.0,
                'glow_intensity': 1.0
            }
        }

        return animations.get(intensity_type, animations['normal'])

    def get_css_animation_values(self, sound_level: float, emotion: str) -> dict:
        """
        Get CSS animation values for HTML/avatar

        Returns:
            dict of CSS property values
        """

        animation_intensity = self.get_animation_intensity(sound_level, emotion)

        return {
            'body_rotation': sound_level * 10,  # Degrees
            'arm_wave_speed': 0.5 + (animation_intensity * 1.5),  # Seconds per cycle
            'head_bob_height': 5 + (animation_intensity * 20),  # Pixels
            'glow_radius': 30 + (animation_intensity * 50),  # Pixels
            'glow_blur': 20 + (animation_intensity * 30),  # Blur filter
            'eye_brightness': 0.5 + (animation_intensity * 0.5),  # Opacity
            'core_pulse_speed': 1.0 + (animation_intensity * 2.0)  # Seconds
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    sr = SoundReactivity()

    # Simulate audio
    test_audio = np.random.randn(16000) * 0.1  # Quiet noise
    level, intensity = sr.analyze_audio_level(test_audio)

    print(f"Sound level: {level:.2f}")
    print(f"Intensity: {intensity}")
    print(f"Animation: {sr.get_animation_intensity(level, 'happy'):.2f}")
    print(f"CSS values: {sr.get_css_animation_values(level, 'happy')}")
