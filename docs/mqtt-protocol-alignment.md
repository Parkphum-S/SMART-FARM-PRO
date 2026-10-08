# MQTT Protocol Alignment

## Current mismatch

- ESP32 status currently uses `esp32_id` and does not publish `timestamp`.
- MQTT contract requires `device_id`, `status`, and `timestamp`.
- Actuator state currently uses `actual_state`, `device_health`, and `updated_at`.
- MQTT contract requires `actuator_id`, `state`, and `timestamp`.

## Decision

The MQTT topic contract remains the source of truth. Firmware must be aligned with the contract before typed payload validation is enabled in the Gateway.
