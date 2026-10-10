from typing import Any

_esp32_status: dict[str, dict[str, Any]] = {}
_sensor_readings: dict[str, dict[str, Any]] = {}
_actuator_states: dict[str, dict[str, Any]] = {}


def _state_key(entity_id: str, payload: dict[str, Any], *, zoned: bool = False) -> str:
    farm_code = payload.get("farm_code")
    zone_code = payload.get("zone_code")

    if isinstance(farm_code, str) and farm_code:
        if zoned and isinstance(zone_code, str) and zone_code:
            return f"{farm_code}/{zone_code}/{entity_id}"
        if not zoned:
            return f"{farm_code}/{entity_id}"

    return entity_id


def set_esp32_status(device_id: str, payload: dict[str, Any]) -> None:
    key = _state_key(device_id, payload)
    _esp32_status[key] = {**payload}


def get_esp32_status() -> dict[str, dict[str, Any]]:
    return {key: dict(value) for key, value in _esp32_status.items()}


def set_sensor_reading(sensor_id: str, payload: dict[str, Any]) -> None:
    key = _state_key(sensor_id, payload, zoned=True)
    _sensor_readings[key] = {**payload}


def get_sensor_readings() -> dict[str, dict[str, Any]]:
    return {key: dict(value) for key, value in _sensor_readings.items()}


def set_actuator_state(actuator_id: str, payload: dict[str, Any]) -> None:
    key = _state_key(actuator_id, payload, zoned=True)
    _actuator_states[key] = {**payload}


def get_actuator_states() -> dict[str, dict[str, Any]]:
    return {key: dict(value) for key, value in _actuator_states.items()}
