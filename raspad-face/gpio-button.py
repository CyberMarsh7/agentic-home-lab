"""
GPIO Push-to-Talk Button Handler for Magic Screen
Monitors physical button on GPIO pin, sends events to frontend via WebSocket
"""

import RPi.GPIO as GPIO
import threading
import json
import logging
from datetime import datetime
from typing import Callable, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PushToTalkButton:
    """Handles physical GPIO button for push-to-talk"""

    def __init__(self, pin: int = 17, on_press: Optional[Callable] = None, on_release: Optional[Callable] = None):
        """
        Initialize GPIO button handler

        Args:
            pin: GPIO pin number (BCM numbering, default 17)
            on_press: Callback when button pressed
            on_release: Callback when button released
        """
        self.pin = pin
        self.on_press = on_press
        self.on_release = on_release
        self.is_pressed = False

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        logger.info(f"🎤 GPIO Button initialized on pin {self.pin}")

    def start(self):
        """Start listening for button events"""
        try:
            GPIO.add_event_detect(
                self.pin,
                GPIO.FALLING,
                callback=self._on_button_change,
                bouncetime=20
            )
            GPIO.add_event_detect(
                self.pin,
                GPIO.RISING,
                callback=self._on_button_change,
                bouncetime=20
            )
            logger.info("✅ GPIO button listener started")
        except Exception as e:
            logger.error(f"❌ Failed to start GPIO listener: {e}")

    def _on_button_change(self, channel):
        """Internal callback for GPIO state change"""
        # Button is active-low (pressed = LOW)
        state = GPIO.input(self.pin)

        if state == 0:  # Button pressed (LOW)
            if not self.is_pressed:
                self.is_pressed = True
                logger.debug("🎤 Button pressed")
                if self.on_press:
                    self.on_press()
        else:  # Button released (HIGH)
            if self.is_pressed:
                self.is_pressed = False
                logger.debug("🎤 Button released")
                if self.on_release:
                    self.on_release()

    def cleanup(self):
        """Clean up GPIO"""
        GPIO.cleanup()
        logger.info("🎤 GPIO cleanup complete")


class WebSocketButtonBridge:
    """Bridge between GPIO button and WebSocket frontend"""

    def __init__(self, socketio):
        """
        Initialize WebSocket bridge

        Args:
            socketio: Flask-SocketIO instance
        """
        self.socketio = socketio
        self.button = None

    def setup_button(self, pin: int = 17):
        """Setup GPIO button with WebSocket callbacks"""
        self.button = PushToTalkButton(
            pin=pin,
            on_press=self._emit_press,
            on_release=self._emit_release
        )
        self.button.start()

    def _emit_press(self):
        """Emit button press to frontend"""
        self.socketio.emit('button_press', {
            'action': 'press',
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)
        logger.info("📤 Sent button_press event")

    def _emit_release(self):
        """Emit button release to frontend"""
        self.socketio.emit('button_release', {
            'action': 'release',
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)
        logger.info("📤 Sent button_release event")

    def cleanup(self):
        """Cleanup GPIO"""
        if self.button:
            self.button.cleanup()


# For testing without Flask
if __name__ == '__main__':
    logger.info("🎤 Testing GPIO button (Ctrl+C to exit)...")
    logger.info("Press the button on GPIO pin 17")

    def on_press():
        print("✅ PRESSED")

    def on_release():
        print("❌ RELEASED")

    button = PushToTalkButton(pin=17, on_press=on_press, on_release=on_release)
    button.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nCleaning up...")
        button.cleanup()
        logger.info("Test complete")
