/*
  Atom Echo Push-to-Talk Firmware
  Records audio when button pressed, sends to RasPad Magic Screen
  Gets response back and plays through speaker

  Designed for complete voice interaction via Atom Echo + battery
*/

#include <M5Atom.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <driver/i2s.h>

// Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* raspad_url = "http://192.168.1.XXX:5000/api/echo-voice";

// I2S configuration for microphone
#define I2S_PORT I2S_NUM_0
#define BUFFER_SIZE 2048

// Button state
bool is_listening = false;
unsigned long button_press_time = 0;

void setup() {
    M5.begin(true, false, true);

    Serial.begin(115200);
    delay(100);

    Serial.println("\n🎤 Atom Echo Magic Screen Controller");
    Serial.println("Initializing...");

    // Setup LED
    M5.dis.setBrightness(50);
    setLED(0xFF0000); // Red = not connected

    // Setup I2S for microphone
    setupI2S();

    // Connect to WiFi
    connectWiFi();

    // Setup button interrupt
    attachInterrupt(digitalPinToInterrupt(39), buttonPressed, FALLING);

    Serial.println("✅ Ready! Press button to talk.");
    setLED(0x00FF00); // Green = ready
}

void loop() {
    M5.update();

    // Check if button is being held
    if (is_listening && digitalRead(39) == HIGH) {
        // Button released
        stopListening();
    }

    delay(10);
}

// ==================== BUTTON HANDLING ====================

void IRAM_ATTR buttonPressed() {
    if (!is_listening && WiFi.status() == WL_CONNECTED) {
        startListening();
    }
}

void startListening() {
    is_listening = true;
    button_press_time = millis();

    Serial.println("🎤 Button pressed - listening...");
    setLED(0x0000FF); // Blue = listening

    // Play start sound
    playTone(1000, 100); // 1kHz beep for 100ms
}

void stopListening() {
    is_listening = false;

    unsigned long duration = millis() - button_press_time;
    Serial.printf("⏹️  Stopped listening (recorded %dms)\n", duration);

    setLED(0xFFFF00); // Yellow = processing

    // Record and send audio
    recordAndSend();

    // Back to ready
    setLED(0x00FF00); // Green = ready
}

// ==================== AUDIO RECORDING ====================

void recordAndSend() {
    Serial.println("📝 Recording audio...");

    uint8_t buffer[BUFFER_SIZE];
    size_t bytes_read = 0;

    // Record for 5 seconds max
    unsigned long start_time = millis();
    unsigned long max_record_time = 5000;

    while (millis() - start_time < max_record_time && is_listening == false) {
        // Read from I2S microphone
        i2s_read(I2S_PORT, buffer, BUFFER_SIZE, &bytes_read, 100);

        if (bytes_read > 0) {
            Serial.printf("📦 Read %d bytes\n", bytes_read);
        }
    }

    Serial.println("✅ Recording complete. Sending to RasPad...");
    sendAudioToRasPad(buffer, bytes_read);
}

void sendAudioToRasPad(uint8_t* audio_data, size_t size) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi not connected!");
        setLED(0xFF0000); // Red = error
        return;
    }

    HTTPClient http;

    // Send audio to RasPad
    http.begin(raspad_url);
    http.addHeader("Content-Type", "audio/wav");

    int httpCode = http.POST(audio_data, size);

    if (httpCode > 0) {
        String response = http.getString();

        Serial.printf("✅ Response from RasPad: %s\n", response.c_str());

        // Play response audio through speaker
        playResponse(response);

        setLED(0x00FF00); // Green = ready
    } else {
        Serial.printf("❌ HTTP error: %d\n", httpCode);
        setLED(0xFF0000); // Red = error
        playTone(500, 500); // Error tone
    }

    http.end();
}

// ==================== AUDIO PLAYBACK ====================

void playResponse(String text) {
    // For now, play a confirmation tone
    // Future: Text-to-speech could go here
    Serial.printf("🔊 Would play: %s\n", text.c_str());

    playTone(2000, 200); // Success beep
    delay(100);
    playTone(2000, 200);
}

void playTone(int frequency, int duration) {
    // Use DAC to play tone
    // This is simplified - real implementation would use proper audio synthesis
    for (int i = 0; i < duration * frequency / 1000; i++) {
        delayMicroseconds(500000 / frequency);
    }
}

// ==================== I2S SETUP ====================

void setupI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_STAND_I2S),
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 1024,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);

    i2s_pin_config_t pin_config = {
        .bck_io_num = 19,
        .ws_io_num = 33,
        .data_out_num = -1,
        .data_in_num = 23
    };

    i2s_set_pin(I2S_PORT, &pin_config);

    Serial.println("✅ I2S microphone configured");
}

// ==================== WIFI ====================

void connectWiFi() {
    Serial.printf("🌐 Connecting to WiFi: %s\n", ssid);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;

        // Blink LED while connecting
        if (attempts % 2 == 0) {
            setLED(0xFF8800); // Orange = connecting
        } else {
            setLED(0xFF0000); // Red
        }
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n✅ Connected! IP: %s\n", WiFi.localIP().toString().c_str());
        setLED(0x00FF00); // Green = ready
    } else {
        Serial.println("\n❌ WiFi connection failed!");
        setLED(0xFF0000); // Red = error
    }
}

// ==================== LED ====================

void setLED(uint32_t color) {
    M5.dis.drawpix(0, color);
}
