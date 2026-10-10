# MQTT Protocol Alignment

## Current implementation

Firmware source is present at `firmware/esp32/SmartFarmESP32.ino`.
The Gateway MQTT client is in `gateway/mqtt_client.py`; Backend MQTT handling
and persistence are implemented under `backend/`.

The protocol uses these payload fields:
- ESP32 status: `device_id`, `status`, `timestamp`.
- Sensor reading: `sensor_id`, `type`, sensor values, `timestamp`.
- Actuator command: `actuator_id`, `command`, `request_id`, `timestamp`.
- Actuator state: `actuator_id`, `state`, `timestamp`.
- Actuator acknowledgement: `actuator_id`, `request_id`, `result`, `timestamp`.

## Decision

Keep the MQTT topic contract as the reference for topic names and required fields.
Firmware, Gateway validators, Backend handlers, tests, and documentation must remain
aligned when the protocol changes.

## Message flow

- Backend publishes actuator commands directly to MQTT.
- ESP32 subscribes to command topics and publishes actuator state and acknowledgements.
- Backend handles status, sensor readings, actuator state, and acknowledgement messages.
- Gateway subscribes to configured topics and validates/logs received messages; it
  does not currently forward Backend actuator commands to ESP32.

## Compatibility notes

The firmware command subscription currently targets
`farm/farm_001/zone/zone_01/actuator/+/command`, with relay identifiers
`relay_01` through `relay_04`. Verify that these match database and API actuator
identifiers before physical actuator tests.

## Verification status

Backend unit tests validate application behavior but do not prove complete end-to-end
delivery. MQTT delivery, PostgreSQL persistence, API readback, and command
acknowledgement still require a separate integration check. Test physical relays
only after confirming electrical and connected-load safety.
