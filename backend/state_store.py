from typing import Any

_esp32_status: dict[str, dict[str, Any]] = {}
_sensor_readings: dict[str, dict[str, Any]] = {}
_actuator_states: dict[str, dict[str, Any]] = {}

def set_esp32_status(device_id: str, payload: dict[str, Any]) -> None:
    _esp32_status[device_id] = payload

def get_esp32_status() -> dict[str, dict[str, Any]]:
    return dict(_esp32_status)

def set_sensor_reading(sensor_id: str, payload: dict[str, Any]) -> None:
    _sensor_readings[sensor_id] = payload

def get_sensor_readings() -> dict[str, dict[str, Any]]:
    return dict(_sensor_readings)

def set_actuator_state(actuator_id: str, payload: dict[str, Any]) -> None:
    _actuator_states[actuator_id] = payload

def get_actuator_states() -> dict[str, dict[str, Any]]:
    return dict(_actuator_states)
