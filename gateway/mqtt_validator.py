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
    if payload["type"] not in {"temperature_humidity", "temperature_humidity_soil"}:
        return False
    if not isinstance(payload["temperature_c"], (int, float)):
        return False
    if not isinstance(payload["humidity_pct"], (int, float)):
        return False
    if "soil_moisture_pct" in payload:
        soil_moisture_pct = payload["soil_moisture_pct"]
        if (
            isinstance(soil_moisture_pct, bool)
            or not isinstance(soil_moisture_pct, (int, float))
            or not 0 <= soil_moisture_pct <= 100
        ):
            return False
    if payload["type"] == "temperature_humidity_soil" and "soil_moisture_pct" not in payload:
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


def validate_actuator_state(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    required = {"actuator_id", "state", "timestamp"}
    if not required.issubset(payload):
        return False

    if not isinstance(payload["actuator_id"], str) or not payload["actuator_id"]:
        return False
    if payload["state"] not in {"on", "off"}:
        return False
    if not isinstance(payload["timestamp"], str):
        return False

    try:
        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        return False

    return True


def validate_actuator_ack(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    required = {"actuator_id", "request_id", "result", "timestamp"}
    if not required.issubset(payload):
        return False

    if not isinstance(payload["actuator_id"], str) or not payload["actuator_id"]:
        return False
    if not isinstance(payload["request_id"], str) or not payload["request_id"]:
        return False
    if payload["result"] not in {"accepted", "rejected"}:
        return False
    if not isinstance(payload["timestamp"], str):
        return False

    try:
        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        return False

    return True


def validate_actuator_command(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    required = {"actuator_id", "command", "request_id", "timestamp"}
    if not required.issubset(payload):
        return False

    if not isinstance(payload["actuator_id"], str) or not payload["actuator_id"]:
        return False
    if payload["command"] not in {"on", "off"}:
        return False
    if not isinstance(payload["request_id"], str) or not payload["request_id"]:
        return False
    if not isinstance(payload["timestamp"], str):
        return False

    try:
        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        return False

    return True
