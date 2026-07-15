#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <ArduinoJson.h>
#include <driver/gpio.h>
#include <esp_rom_sys.h>
#include <math.h>
#include "protocol.h"

using namespace Plane;

// motor_driver_回路図.pdf / XIAO ESP32C3 D0..D10 pin assignment
constexpr uint8_t PIN_MO = D0;       // SLA7078 MO (monitor input)
constexpr uint8_t PIN_M2 = D1;
constexpr uint8_t PIN_CLOCK = D2;
constexpr uint8_t PIN_DIRECTION = D3;
constexpr uint8_t PIN_FLAG = D4;     // SLA7078 FLAG input
constexpr uint8_t PIN_SYNC = D5;
constexpr uint8_t PIN_RESET = D6;
constexpr uint8_t PIN_M3 = D7;
constexpr uint8_t PIN_M1 = D8;
constexpr uint8_t PIN_DRIVER_SLEEP = D9;  // ref/sleep_mcu PMOS control
constexpr uint8_t PIN_STATUS_LED = D10;

#ifndef MOTOR_FULL_STEPS_PER_REV
#define MOTOR_FULL_STEPS_PER_REV 200
#endif
#ifndef MOTOR_MICROSTEPS
#define MOTOR_MICROSTEPS 1
#endif
#ifndef MOTOR_DIRECTION_INVERT
#define MOTOR_DIRECTION_INVERT 0
#endif
#ifndef MOTOR_MAX_OUTPUT_SPEED_DEG_SEC
#define MOTOR_MAX_OUTPUT_SPEED_DEG_SEC 300
#endif

constexpr float STEPS_PER_DEGREE =
    (MOTOR_FULL_STEPS_PER_REV * MOTOR_MICROSTEPS) / 360.0f;
constexpr uint32_t MOTOR_TIMER_HZ = 40000;
constexpr float CONTINUOUS_CW_COMMAND_DEG = 999.0f;
constexpr float CONTINUOUS_CCW_COMMAND_DEG = -999.0f;

struct LightLink {
  bool online = false;
  bool unstable = false;
  bool awaiting = false;
  uint8_t retries = 0;
  uint32_t sentAt = 0;
  uint32_t lastAck = 0;
  uint32_t pendingSeq = 0;
  uint32_t remoteUptime = 0;
} light;

MotorPayload motorSet{};
LightPayload lightSet{};
uint32_t sequence = 0;
uint32_t lastPeriodic = 0;
uint32_t espInterval = 10000;
uint32_t retryTimeout = 500;
uint8_t maxRetries = 5;
uint32_t pcCommunicationTimeoutMs = 22000;
uint32_t lastPcPacketAt = 0;
bool pcSafetyStopActive = true;
String line;

volatile int64_t physicalSteps = 0;
volatile int64_t zeroOffsetSteps = 0;
volatile int64_t targetSteps = 0;
volatile uint32_t stepRateMilliHz = 0;
volatile uint32_t stepPhase = 0;
volatile int8_t jogDirection = 0;  // -1: CCW, +1: CW, 0: position mode
portMUX_TYPE motorMux = portMUX_INITIALIZER_UNLOCKED;
hw_timer_t *motorTimer = nullptr;
float commandedSpeedDegSec = 0.0f;
uint32_t motorLastApplied = 0;
bool motorCalibrationMode = false;
bool motorOriginSet = false;
bool originWarningSent = false;
bool emergencyStopActive = false;
TaskHandle_t communicationTaskHandle = nullptr;
void communicationTask(void *parameter);
void sendLight(bool retry = false);

float normalizeAngle(float angleDeg) {
  float wrapped = fmodf(angleDeg, 360.0f);
  return wrapped < 0 ? wrapped + 360.0f : wrapped;
}

float currentAngleDeg() {
  portENTER_CRITICAL(&motorMux);
  int64_t position = physicalSteps;
  int64_t zero = zeroOffsetSteps;
  portEXIT_CRITICAL(&motorMux);
  return normalizeAngle((position - zero) / STEPS_PER_DEGREE);
}

void jsonEvent(const char *event, const char *device = "") {
  JsonDocument d;
  d["type"] = "event";
  d["event"] = event;
  if (*device) {
    d["device"] = device;
  }
  serializeJson(d, Serial);
  Serial.println();
}

void IRAM_ATTR onMotorTimer() {
  portENTER_CRITICAL_ISR(&motorMux);
  int8_t direction = jogDirection;
  if (direction == 0) {
    if (physicalSteps < targetSteps) {
      direction = 1;
    } else if (physicalSteps > targetSteps) {
      direction = -1;
    }
    else {
      stepPhase = 0;
      portEXIT_CRITICAL_ISR(&motorMux);
      return;
    }
  }
  stepPhase += stepRateMilliHz;
  constexpr uint32_t PHASE_LIMIT = MOTOR_TIMER_HZ * 1000UL;
  if (stepRateMilliHz && stepPhase >= PHASE_LIMIT) {
    stepPhase -= PHASE_LIMIT;
    bool cw = direction > 0;
    gpio_set_level((gpio_num_t)PIN_DIRECTION,
                   (cw ^ MOTOR_DIRECTION_INVERT) ? 0 : 1);
    esp_rom_delay_us(1);  // CW/CCW setup time before CLOCK
    gpio_set_level((gpio_num_t)PIN_CLOCK, 1);
    esp_rom_delay_us(2);  // SLA7078 minimum CLOCK high width
    gpio_set_level((gpio_num_t)PIN_CLOCK, 0);
    physicalSteps += direction;
  }
  portEXIT_CRITICAL_ISR(&motorMux);
}

void updateStepRate(float speedDegSec) {
  uint32_t rate = (uint32_t)llroundf(speedDegSec * STEPS_PER_DEGREE * 1000.0f);
  portENTER_CRITICAL(&motorMux);
  stepRateMilliHz = rate;
  portEXIT_CRITICAL(&motorMux);
}

void applyMotorTarget(float angleDeg, float speedDegSec) {
  if (!motorOriginSet) {
    if (!originWarningSent) {
      jsonEvent("motor_command_blocked_origin_unset", "motor");
      originWarningSent = true;
    }
    return;
  }
  const bool continuousCw =
      fabsf(angleDeg - CONTINUOUS_CW_COMMAND_DEG) < 0.001f;
  const bool continuousCcw =
      fabsf(angleDeg - CONTINUOUS_CCW_COMMAND_DEG) < 0.001f;
  const bool continuous = continuousCw || continuousCcw;
  const float normalizedTarget = continuousCw
                                     ? CONTINUOUS_CW_COMMAND_DEG
                                 : continuousCcw
                                     ? CONTINUOUS_CCW_COMMAND_DEG
                                     : normalizeAngle(angleDeg);
  motorSet.angleDeg = normalizedTarget;
  motorSet.speedDegSec = min(fabsf(speedDegSec),
                             (float)MOTOR_MAX_OUTPUT_SPEED_DEG_SEC);
  commandedSpeedDegSec = motorSet.speedDegSec;
  portENTER_CRITICAL(&motorMux);
  if (continuous) {
    // +999/-999 are command values, not physical target angles.
    jogDirection = continuousCw ? 1 : -1;
    targetSteps = physicalSteps;
  } else {
    jogDirection = 0;
    const int64_t revolutionSteps = llroundf(360.0f * STEPS_PER_DEGREE);
    int64_t logicalSteps = physicalSteps - zeroOffsetSteps;
    int64_t currentWithinRevolution = logicalSteps % revolutionSteps;
    if (currentWithinRevolution < 0) {
      currentWithinRevolution += revolutionSteps;
    }
    int64_t requestedWithinRevolution =
        llroundf(normalizedTarget * STEPS_PER_DEGREE) % revolutionSteps;
    int64_t delta = requestedWithinRevolution - currentWithinRevolution;
    if (delta > revolutionSteps / 2) {
      delta -= revolutionSteps;
    }
    if (delta < -revolutionSteps / 2) {
      delta += revolutionSteps;
    }
    targetSteps = physicalSteps + delta;
  }
  portEXIT_CRITICAL(&motorMux);
  updateStepRate(commandedSpeedDegSec);
  motorLastApplied = millis();
}

void stopMotorImmediatelyForPcLoss() {
  portENTER_CRITICAL(&motorMux);
  jogDirection = 0;
  targetSteps = physicalSteps;
  stepRateMilliHz = 0;
  stepPhase = 0;
  portEXIT_CRITICAL(&motorMux);
  commandedSpeedDegSec = 0.0f;
  motorSet.speedDegSec = 0.0f;
  motorCalibrationMode = false;
  motorLastApplied = millis();
}

void activateEmergencyStop() {
  emergencyStopActive = true;
  stopMotorImmediatelyForPcLoss();
  lightSet.firstStar = 0;
  lightSet.stars = 0;
  lightSet.patterns = 0;
  lightSet.fade = 0;
  sendLight();
  jsonEvent("emergency_stop_activated", "system");
}

void updatePcSafetyWatchdog() {
  const bool timedOut = lastPcPacketAt == 0 ||
                        millis() - lastPcPacketAt > pcCommunicationTimeoutMs;
  if (timedOut && !pcSafetyStopActive) {
    pcSafetyStopActive = true;
    stopMotorImmediatelyForPcLoss();
    jsonEvent("pc_communication_lost_motor_stopped", "motor");
  }
}

void applyMotorCalibration(const char *action, float speedDegSec,
                           float valueDeg) {
  commandedSpeedDegSec = min(fabsf(speedDegSec),
                              (float)MOTOR_MAX_OUTPUT_SPEED_DEG_SEC);
  updateStepRate(commandedSpeedDegSec);
  portENTER_CRITICAL(&motorMux);
  if (!strcmp(action, "jog_cw")) {
    jogDirection = 1;
  } else if (!strcmp(action, "jog_ccw")) {
    jogDirection = -1;
  } else if (!strcmp(action, "stop")) {
    jogDirection = 0;
    targetSteps = physicalSteps;
    commandedSpeedDegSec = 0;
    stepRateMilliHz = 0;
  } else if (!strcmp(action, "move_relative")) {
    jogDirection = 0;
    targetSteps = physicalSteps + llroundf(valueDeg * STEPS_PER_DEGREE);
  } else if (!strcmp(action, "set_zero")) {
    jogDirection = 0;
    targetSteps = physicalSteps;
    zeroOffsetSteps = physicalSteps;
    commandedSpeedDegSec = 0;
    stepRateMilliHz = 0;
    motorOriginSet = true;
    originWarningSent = false;
  } else if (!strcmp(action, "set_angle")) {
    jogDirection = 0;
    targetSteps = physicalSteps;
    zeroOffsetSteps = physicalSteps -
                      llroundf(normalizeAngle(valueDeg) * STEPS_PER_DEGREE);
    commandedSpeedDegSec = 0;
    stepRateMilliHz = 0;
    motorOriginSet = true;
    originWarningSent = false;
  }
  portEXIT_CRITICAL(&motorMux);
  motorLastApplied = millis();
  if (motorOriginSet &&
      (!strcmp(action, "set_zero") || !strcmp(action, "set_angle"))) {
    jsonEvent("motor_origin_set", "motor");
  }
}

void sendLight(bool retry) {
  lightSet.heartbeatTimeoutMs = max((uint32_t)3000, espInterval * 2 + 2000);
  lightSet.h = header(Type::LIGHT_SET, sizeof(lightSet),
                      retry ? light.pendingSeq : ++sequence);
  light.pendingSeq = lightSet.h.seq;
  esp_now_send(MAC_LIGHT, reinterpret_cast<uint8_t *>(&lightSet),
               sizeof(lightSet));
  light.awaiting = true;
  light.sentAt = millis();
  if (!retry) {
    light.retries = 0;
  }
}

void emitStatus() {
  JsonDocument d;
  d["type"] = "status";
  d["uptime_ms"] = millis();
  d["motor_calibration_mode"] = motorCalibrationMode;
  d["motor_origin_set"] = motorOriginSet;
  d["emergency_stop"] = emergencyStopActive;
  d["pc_safety_stop"] = pcSafetyStopActive;
  d["pc_timeout_ms"] = pcCommunicationTimeoutMs;
  auto mlink = d["motor"].to<JsonObject>();
  mlink["online"] = true;
  mlink["unstable"] = false;
  // The motor driver is on this MCU, so every status cycle is a local heartbeat.
  mlink["last_ack_ms"] = millis();
  mlink["retries"] = 0;
  auto llink = d["light"].to<JsonObject>();
  llink["online"] = light.online;
  llink["unstable"] = light.unstable;
  llink["last_ack_ms"] = light.lastAck;
  llink["uptime_ms"] = light.remoteUptime;
  llink["retries"] = light.retries;
  auto m = d["actual"]["motor"].to<JsonObject>();
  int8_t motionJog;
  int64_t motionPhysical, motionTarget, motionZero;
  portENTER_CRITICAL(&motorMux);
  motionJog = jogDirection;
  motionPhysical = physicalSteps;
  motionTarget = targetSteps;
  motionZero = zeroOffsetSteps;
  portEXIT_CRITICAL(&motorMux);
  m["angle"] = currentAngleDeg();
  // Calibration jog reports a signed speed: CW positive, CCW negative.
  m["speed"] = motorCalibrationMode && motionJog < 0
                   ? -commandedSpeedDegSec
                   : commandedSpeedDegSec;
  bool relativeMoving = motorCalibrationMode && motionJog == 0 &&
                        motionPhysical != motionTarget && stepRateMilliHz > 0;
  m["motion"] = motionJog > 0 ? "jog_cw"
                  : motionJog < 0 ? "jog_ccw"
                  : relativeMoving ? "relative"
                                   : "stopped";
  m["target_angle"] = normalizeAngle(
      (motionTarget - motionZero) / STEPS_PER_DEGREE);
  m["continuous_cw"] =
      fabsf(motorSet.angleDeg - CONTINUOUS_CW_COMMAND_DEG) < 0.001f;
  m["continuous_ccw"] =
      fabsf(motorSet.angleDeg - CONTINUOUS_CCW_COMMAND_DEG) < 0.001f;
  auto q = d["actual"]["light"].to<JsonObject>();
  q["first"] = lightSet.firstStar;
  q["stars"] = lightSet.stars;
  q["patterns"] = lightSet.patterns;
  d["motor_driver_flag"] = digitalRead(PIN_FLAG) == HIGH ? "active" : "normal";
  d["cores"]["communication"] = 0;
  d["cores"]["motor"] = 0;
  serializeJson(d, Serial);
  Serial.println();
}

void onReceive(const uint8_t *, const uint8_t *data, int len) {
  if (len != static_cast<int>(sizeof(AckPayload))) {
    return;
  }
  AckPayload a;
  memcpy(&a, data, sizeof(a));
  if (!valid(a.h, len) || a.h.type != Type::LIGHT_ACK ||
      a.h.seq != light.pendingSeq) {
    return;
  }
  bool recovered = !light.online || light.unstable;
  light.online = true;
  light.unstable = false;
  light.awaiting = false;
  light.lastAck = millis();
  light.remoteUptime = a.uptimeMs;
  lightSet.firstStar = a.firstStar;
  lightSet.stars = a.stars;
  lightSet.patterns = a.patterns;
  if (recovered) {
    jsonEvent("communication_recovered", "light");
  }
}

void handleLine() {
  JsonDocument d;
  if (deserializeJson(d, line)) {
    jsonEvent("invalid_json");
    return;
  }
  const bool recovered = pcSafetyStopActive;
  lastPcPacketAt = millis();
  pcSafetyStopActive = false;
  if (recovered) {
    jsonEvent("pc_communication_recovered", "motor");
  }
  const char *cmd = d["cmd"] | "";
  if (!strcmp(cmd, "emergency_stop")) {
    activateEmergencyStop();
  } else if (!strcmp(cmd, "emergency_stop_release")) {
    emergencyStopActive = false;
    stopMotorImmediatelyForPcLoss();
    jsonEvent("emergency_stop_released", "system");
  } else if (!strcmp(cmd, "set")) {
    if (emergencyStopActive) {
      stopMotorImmediatelyForPcLoss();
      if (lightSet.firstStar || lightSet.stars || lightSet.patterns) {
        lightSet.firstStar = 0;
        lightSet.stars = 0;
        lightSet.patterns = 0;
        lightSet.fade = 0;
        sendLight();
      }
      jsonEvent("command_blocked_emergency_stop", "system");
      return;
    }
    float angle = d["motor"]["angle"] | motorSet.angleDeg;
    float speed = d["motor"]["speed"] | motorSet.speedDegSec;
    if (!motorCalibrationMode) {
      applyMotorTarget(angle, speed);
    }
    lightSet.firstStar = d["light"]["first"] | false;
    lightSet.stars = d["light"]["stars"] | false;
    lightSet.patterns = 0;
    for (int i = 0; i < 8; ++i) {
      if (d["light"]["patterns"][i] | false) {
        lightSet.patterns |= 1 << i;
      }
    }
    lightSet.fade = d["light"]["fade"] | false;
    sendLight();
  } else if (!strcmp(cmd, "config")) {
    espInterval = constrain((uint32_t)(d["esp_interval_ms"] | espInterval),
                            100, 3600000);
    retryTimeout = constrain((uint32_t)(d["retry_timeout_ms"] | retryTimeout),
                             100, 10000);
    maxRetries = constrain((uint8_t)(d["max_retries"] | maxRetries), 1, 10);
    pcCommunicationTimeoutMs = constrain(
        (uint32_t)(d["pc_timeout_ms"] | pcCommunicationTimeoutMs),
        3000, 3600000);
  } else if (!strcmp(cmd, "motor_cal")) {
    if (emergencyStopActive) {
      stopMotorImmediatelyForPcLoss();
      jsonEvent("motor_calibration_blocked_emergency_stop", "motor");
      return;
    }
    const char *action = d["action"] | "";
    if (!strcmp(action, "exit")) {
      motorCalibrationMode = false;
      portENTER_CRITICAL(&motorMux);
      jogDirection = 0;
      targetSteps = physicalSteps;
      stepRateMilliHz = 0;
      portEXIT_CRITICAL(&motorMux);
      commandedSpeedDegSec = 0;
      jsonEvent("motor_calibration_finished", "motor");
    } else {
      motorCalibrationMode = true;
      applyMotorCalibration(action, d["speed"] | 0.0f, d["value"] | 0.0f);
      jsonEvent("motor_calibration_command", "motor");
    }
  } else if (!strcmp(cmd, "send_now")) {
    sendLight();
    motorLastApplied = millis();
  } else if (!strcmp(cmd, "ping")) {
    Serial.println("{\"type\":\"pong\"}");
  }
}

void retryLight() {
  if (!light.awaiting || millis() - light.sentAt < retryTimeout) {
    return;
  }
  if (light.retries < maxRetries) {
    ++light.retries;
    light.unstable = true;
    light.online = true;
    jsonEvent("communication_unstable", "light");
    sendLight(true);
  } else {
    light.awaiting = false;
    light.online = false;
    light.unstable = false;
    jsonEvent("communication_lost", "light");
  }
}

void setupMotorHardware() {
  pinMode(PIN_MO, INPUT);
  pinMode(PIN_FLAG, INPUT);  // 10 kΩ external pull-down on the circuit board
  pinMode(PIN_M1, OUTPUT);
  pinMode(PIN_M2, OUTPUT);
  pinMode(PIN_M3, OUTPUT);
  pinMode(PIN_DIRECTION, OUTPUT);
  pinMode(PIN_SYNC, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);
  pinMode(PIN_DRIVER_SLEEP, OUTPUT);
  pinMode(PIN_RESET, OUTPUT);
  pinMode(PIN_CLOCK, OUTPUT);
  digitalWrite(PIN_CLOCK, LOW);
  digitalWrite(PIN_M1, LOW);
  digitalWrite(PIN_M2, LOW);
  digitalWrite(PIN_M3, LOW);
  digitalWrite(PIN_SYNC, LOW);
  // LOW turns the PMOS on and raises Ref/Sleep1 into the Sleep1 range.
  // Keep it HIGH for normal operation (PMOS off).
  digitalWrite(PIN_DRIVER_SLEEP, HIGH);
  delayMicroseconds(100);  // Datasheet minimum wake-up time before CLOCK.
  // SLA7078 RESET is active-high. Reset once, then keep LOW for operation.
  digitalWrite(PIN_RESET, HIGH);
  delayMicroseconds(5);
  digitalWrite(PIN_RESET, LOW);
  delayMicroseconds(10);
  digitalWrite(PIN_STATUS_LED, HIGH);
  motorTimer = timerBegin(0, 80, true);  // 1 MHz timer clock
  timerAttachInterrupt(motorTimer, &onMotorTimer, true);
  timerAlarmWrite(motorTimer, 1000000UL / MOTOR_TIMER_HZ, true);
  timerAlarmEnable(motorTimer);
  motorLastApplied = millis();
}

void setup() {
  Serial.begin(115200);
  setupMotorHardware();
  WiFi.mode(WIFI_STA);
  esp_wifi_set_mac(WIFI_IF_STA, MAC_COORD);
  esp_wifi_set_channel(CHANNEL, WIFI_SECOND_CHAN_NONE);
  if (esp_now_init() != ESP_OK) {
    jsonEvent("esp_now_init_failed");
    return;
  }
  esp_now_register_recv_cb(onReceive);
  esp_now_peer_info_t peer{};
  memcpy(peer.peer_addr, MAC_LIGHT, 6);
  peer.channel = CHANNEL;
  peer.encrypt = false;
  esp_now_add_peer(&peer);
  Serial.println("{\"type\":\"hello\",\"device\":\"coordinator_motor\",\"protocol\":1}");
  sendLight();
  // ESP32C3 has one CPU core. Communication runs as a normal FreeRTOS task,
  // while motor CLOCK generation remains isolated in the hardware timer ISR.
  xTaskCreate(communicationTask, "communication", 8192, nullptr, 2,
              &communicationTaskHandle);
}

void communicationTask(void *) {
  for (;;) {
    while (Serial.available()) {
      char c = Serial.read();
      if (c == '\n') {
        handleLine();
        line = "";
      } else if (c != '\r' && line.length() < 1024) {
        line += c;
      }
    }
    if (millis() - lastPeriodic >= espInterval) {
      sendLight();
      lastPeriodic = millis();
    }
    retryLight();
    updatePcSafetyWatchdog();
    static uint32_t lastStatus = 0;
    if (millis() - lastStatus >= 250) {
      lastStatus = millis();
      emitStatus();
    }
    vTaskDelay(pdMS_TO_TICKS(1));
  }
}

void loop() {
  // The communication task handles application work. Motor CLOCK generation
  // is independent of task scheduling because it runs in the timer ISR.
  delay(1000);
}
