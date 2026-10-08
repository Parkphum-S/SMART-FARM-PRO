from datetime import datetime


def validate_payload(payload: dict) -> bool:
    return isinstance(payload, dict) and bool(payload)


def validate_sensor_reading(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    required = {
        "sensor_id",
        "type",
        "temperature_c",
        "humidity_pct",
        "timestamp",
    }
    if not required.issubset(payload):
        return False

    if not isinstance(payload["sensor_id"], str) or not payload["sensor_id"]:
        return False
    if payload["type"] != "temperature_humidity":
        return False
    if not isinstance(payload["temperature_c"], (int, float)):
        return False
    if not isinstance(payload["humidity_pct"], (int, float)):
        return False
    if not isinstance(payload["timestamp"], str):
        return False

    try:
        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        return False

    return True


def validate_esp32_status(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    required = {"device_id", "status", "timestamp"}
    if not required.issubset(payload):
        return False

    if not isinstance(payload["device_id"], str) or not payload["device_id"]:
        return False
    if payload["status"] not in {"online", "offline"}:
        return False
    if not isinstance(payload["timestamp"], str):
        return False

    try:
        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        return False

    return True
