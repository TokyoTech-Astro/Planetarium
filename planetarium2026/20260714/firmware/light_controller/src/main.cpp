#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>

#include "protocol.h"

using namespace Plane;

// seiza_ittose_回路図.pdf / XIAO ESP32C3 pin assignment.
// The TC5626B3A inputs drive constellation outputs 1..8.
constexpr uint8_t CONSTELLATION_PINS[8] = {
    D7, D8, D9, D10, D5, D4, D3, D2,
};
constexpr uint8_t STARS_PIN = D0;
constexpr uint8_t FIRST_STAR_PIN = D1;
constexpr uint8_t STATUS_LED_PIN = D6;
constexpr bool STARS_ACTIVE_HIGH = false;
constexpr bool FIRST_STAR_ACTIVE_HIGH = true;
constexpr bool CONSTELLATIONS_ACTIVE_HIGH = true;

constexpr uint32_t DEFAULT_HEARTBEAT_TIMEOUT_MS = 22000;
constexpr uint32_t MIN_HEARTBEAT_TIMEOUT_MS = 3000;
constexpr uint32_t CONNECTED_BLINK_INTERVAL_MS = 1000;
constexpr uint32_t DISCONNECTED_BLINK_INTERVAL_MS = 120;
constexpr uint32_t LIGHT_FADE_DURATION_MS = 1200;

LightPayload current{};
uint32_t lastCoordinatorRx = 0;
uint32_t heartbeatTimeoutMs = DEFAULT_HEARTBEAT_TIMEOUT_MS;
uint32_t lastLedToggle = 0;
bool statusLedOn = false;
uint8_t brightness[10]{};
uint8_t fadeStart[10]{};
uint8_t fadeTarget[10]{};
uint8_t pwmAccumulator[10]{};
uint32_t fadeStartedAt = 0;
bool fadeActive = false;

uint8_t outputPin(int index) {
  if (index == 0) return FIRST_STAR_PIN;
  if (index == 1) return STARS_PIN;
  return CONSTELLATION_PINS[index - 2];
}

bool outputActiveHigh(int index) {
  if (index == 0) return FIRST_STAR_ACTIVE_HIGH;
  if (index == 1) return STARS_ACTIVE_HIGH;
  return CONSTELLATIONS_ACTIVE_HIGH;
}

bool requestedOutput(int index, const LightPayload &value) {
  if (index == 0) return value.firstStar;
  if (index == 1) return value.stars;
  return value.patterns & (1 << (index - 2));
}

void setOutput(uint8_t pin, bool on, bool activeHigh) {
  digitalWrite(pin, (on == activeHigh) ? HIGH : LOW);
}

void applyLightOutputs() {
  for (int index = 0; index < 10; ++index) {
    brightness[index] = requestedOutput(index, current) ? 255 : 0;
    fadeTarget[index] = brightness[index];
    setOutput(outputPin(index), brightness[index] != 0,
              outputActiveHigh(index));
  }
  fadeActive = false;
}

void sendAcknowledgement(uint32_t sequence) {
  AckPayload acknowledgement{};
  acknowledgement.h =
      header(Type::LIGHT_ACK, sizeof(acknowledgement), sequence);
  acknowledgement.applied = 1;
  acknowledgement.firstStar = current.firstStar;
  acknowledgement.stars = current.stars;
  acknowledgement.patterns = current.patterns;
  acknowledgement.uptimeMs = millis();

  esp_now_send(MAC_COORD,
               reinterpret_cast<uint8_t *>(&acknowledgement),
               sizeof(acknowledgement));
}

void beginLightTransition(bool useFade) {
  if (!useFade) {
    applyLightOutputs();
    return;
  }
  for (int index = 0; index < 10; ++index) {
    fadeStart[index] = brightness[index];
    fadeTarget[index] = requestedOutput(index, current) ? 255 : 0;
  }
  fadeStartedAt = millis();
  fadeActive = true;
}

void updateLightFade(uint32_t now) {
  if (fadeActive) {
    float progress = min(1.0f, (now - fadeStartedAt) /
                                   static_cast<float>(LIGHT_FADE_DURATION_MS));
    // Smoothstep avoids an abrupt start/end; gamma gives a natural visual fade.
    float smooth = progress * progress * (3.0f - 2.0f * progress);
    float shaped = powf(smooth, 1.8f);
    for (int index = 0; index < 10; ++index) {
      brightness[index] = lroundf(fadeStart[index] +
          (fadeTarget[index] - fadeStart[index]) * shaped);
    }
    if (progress >= 1.0f) fadeActive = false;
  }
  // 1 kHz pulse-density modulation supports all ten outputs on ESP32-C3,
  // whose hardware LEDC channel count is smaller than the output count.
  for (int index = 0; index < 10; ++index) {
    uint16_t sum = pwmAccumulator[index] + brightness[index];
    pwmAccumulator[index] = static_cast<uint8_t>(sum);
    setOutput(outputPin(index), sum > 255, outputActiveHigh(index));
  }
}

void receiveEspNow(const uint8_t *, const uint8_t *data, int length) {
  if (length != static_cast<int>(sizeof(LightPayload))) {
    return;
  }

  LightPayload received{};
  memcpy(&received, data, sizeof(received));

  if (!valid(received.h, length) || received.h.type != Type::LIGHT_SET) {
    return;
  }

  current = received;
  lastCoordinatorRx = millis();
  heartbeatTimeoutMs =
      max(MIN_HEARTBEAT_TIMEOUT_MS, received.heartbeatTimeoutMs);

  beginLightTransition(received.fade != 0);
  sendAcknowledgement(received.h.seq);

  Serial.printf(
      "LIGHT seq=%lu first=%u stars=%u constellations=0x%02X "
      "timeout=%lu ms\n",
      received.h.seq,
      current.firstStar,
      current.stars,
      current.patterns,
      heartbeatTimeoutMs);
}

void setup() {
  Serial.begin(115200);

  pinMode(FIRST_STAR_PIN, OUTPUT);
  pinMode(STARS_PIN, OUTPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  for (uint8_t pin : CONSTELLATION_PINS) {
    pinMode(pin, OUTPUT);
  }

  applyLightOutputs();
  digitalWrite(STATUS_LED_PIN, LOW);

  WiFi.mode(WIFI_STA);
  esp_wifi_set_mac(WIFI_IF_STA, MAC_LIGHT);
  esp_wifi_set_channel(CHANNEL, WIFI_SECOND_CHAN_NONE);

  esp_now_init();
  esp_now_register_recv_cb(receiveEspNow);

  esp_now_peer_info_t coordinatorPeer{};
  memcpy(coordinatorPeer.peer_addr, MAC_COORD, sizeof(MAC_COORD));
  coordinatorPeer.channel = CHANNEL;
  esp_now_add_peer(&coordinatorPeer);

  Serial.println("LIGHT READY");
}

void loop() {
  const uint32_t now = millis();
  const bool connected =
      lastCoordinatorRx != 0 &&
      now - lastCoordinatorRx <= heartbeatTimeoutMs;
  updateLightFade(now);
  const uint32_t blinkInterval = connected ? CONNECTED_BLINK_INTERVAL_MS
                                           : DISCONNECTED_BLINK_INTERVAL_MS;
  if (now - lastLedToggle >= blinkInterval) {
    lastLedToggle = now;
    statusLedOn = !statusLedOn;
    digitalWrite(STATUS_LED_PIN, statusLedOn ? HIGH : LOW);
  }

  delay(1);
}
