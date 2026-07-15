#pragma once

#include <Arduino.h>

namespace Plane {

constexpr uint32_t MAGIC = 0x504C414E;
constexpr uint8_t VERSION = 3;
constexpr uint8_t CHANNEL = 1;

constexpr uint8_t MAC_COORD[6] = {0x02, 0x50, 0x4C,
                                  0x41, 0x4E, 0x01};
constexpr uint8_t MAC_LIGHT[6] = {0x02, 0x50, 0x4C,
                                  0x41, 0x4E, 0x02};
constexpr uint8_t MAC_MOTOR[6] = {0x02, 0x50, 0x4C,
                                  0x41, 0x4E, 0x03};

enum class Type : uint8_t {
  MOTOR_SET = 1,
  LIGHT_SET = 2,
  MOTOR_ACK = 3,
  LIGHT_ACK = 4,
  PING = 5,
  MOTOR_CAL = 6,
};

enum class MotorCalCommand : uint8_t {
  JOG_CW = 1,
  JOG_CCW = 2,
  STOP = 3,
  MOVE_RELATIVE = 4,
  SET_ZERO = 5,
  SET_CURRENT_ANGLE = 6,
};

struct __attribute__((packed)) Header {
  uint32_t magic;
  uint8_t version;
  Type type;
  uint16_t size;
  uint32_t seq;
};

struct __attribute__((packed)) MotorPayload {
  Header h;
  float angleDeg;
  float speedDegSec;
};

struct __attribute__((packed)) MotorCalPayload {
  Header h;
  MotorCalCommand command;
  uint8_t reserved[3];
  float speedDegSec;
  float valueDeg;
};

struct __attribute__((packed)) LightPayload {
  Header h;
  uint8_t firstStar;
  uint8_t stars;
  uint8_t patterns;
  uint8_t fade;  // 1 only for automatic timeline changes during playback
  uint32_t heartbeatTimeoutMs;
};

struct __attribute__((packed)) AckPayload {
  Header h;
  uint8_t applied;
  uint8_t reserved[3];
  float angleDeg;
  float speedDegSec;
  uint8_t firstStar;
  uint8_t stars;
  uint8_t patterns;
  uint8_t reserved2;
  uint32_t uptimeMs;
};

inline bool valid(const Header &h, size_t len) {
  return h.magic == MAGIC && h.version == VERSION && h.size == len;
}

inline Header header(Type type, uint16_t size, uint32_t sequence) {
  return {MAGIC, VERSION, type, size, sequence};
}

}  // namespace Plane
