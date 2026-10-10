# Smart Farm Pro MQTT Topic Contract

## 1. Topic Namespace

All Smart Farm MQTT topics use:

farm/{farm_id}/...

Example:

farm/farm_001/...

---

## 2. Device Status

### ESP32 Status

ESP32 publishes:

farm/{farm_id}/esp32/{device_id}/status

Payload:

{
  "device_id": "esp32_001",
  "status": "online",
  "timestamp": "2026-10-08T00:00:00Z"
}

---

## 3. Sensor Reading

### Zone Sensor

farm/{farm_id}/zone/{zone_id}/sensor/{sensor_id}/reading

Payload:

{
  "sensor_id": "dht11_001",
  "type": "temperature_humidity",
  "temperature_c": 28.5,
  "humidity_pct": 72.0,
  "timestamp": "2026-10-08T00:00:00Z"
}

---

## 4. Actuator Command

Backend publishes:

farm/{farm_id}/zone/{zone_id}/actuator/{actuator_id}/command

Payload:

{
  "actuator_id": "relay_01",
  "command": "on",
  "request_id": "req-001",
  "timestamp": "2026-10-08T00:00:00Z"
}

---

## 5. Actuator State

ESP32 publishes:

farm/{farm_id}/zone/{zone_id}/actuator/{actuator_id}/state

Payload:

{
  "actuator_id": "pump_001",
  "state": "on",
  "timestamp": "2026-10-08T00:00:00Z"
}

---

## 6. Actuator Acknowledgement

ESP32 publishes:

farm/{farm_id}/zone/{zone_id}/actuator/{actuator_id}/ack

Payload:

{
  "actuator_id": "pump_001",
  "request_id": "req-001",
  "result": "accepted",
  "timestamp": "2026-10-08T00:00:00Z"
}

---

## 7. Gateway Responsibilities

Gateway:

- Subscribe to actuator commands.
- Receive sensor readings.
- Receive ESP32 status.
- Validate and log received messages; the current implementation does not forward commands.
- Do not access topics outside its assigned farm/zone scope.
- Use MQTT authentication credentials from environment variables.

---

## 8. Backend Responsibilities

Backend:
- Publishes actuator commands directly to MQTT.
- Processes sensor readings, device status, actuator state, and acknowledgements.
- Checks user permissions and farm membership before actuator control.
- Persists actuator commands before publishing them.

## 9. Timestamp

All timestamps use ISO 8601 UTC.

Example:

2026-10-08T00:00:00Z

---

## 10. Request ID

Commands that require acknowledgement must contain a unique `request_id`.

The same `request_id` must be returned in the corresponding acknowledgement.

---

## 11. Topic Design Rules

- Use lowercase identifiers.
- Use `/` as topic hierarchy separator.
- Do not place secrets in MQTT topics.
- Device IDs and zone IDs must be stable identifiers.
- Payloads are JSON encoded using UTF-8.

## 12. Verification boundary

Passing unit tests does not prove end-to-end MQTT delivery or database readback.
Verify ESP32 publishing, MQTT delivery, Backend persistence, API readback, and
command acknowledgement separately before declaring integration complete.
