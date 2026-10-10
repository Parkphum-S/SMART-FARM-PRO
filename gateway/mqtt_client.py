import paho.mqtt.client as mqtt

from mqtt_parser import parse_payload
from mqtt_validator import (
    validate_actuator_ack,
    validate_actuator_command,
    validate_actuator_state,
    validate_esp32_status,
    validate_sensor_reading,
)
from mqtt_config import (
    MQTT_HOST,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_USERNAME,
)


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="smartfarm_gateway",
)

client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

TOPICS = (
    "farm/farm_001/esp32/+/status",
    "farm/farm_001/zone/+/sensor/+/reading",
    "farm/farm_001/zone/+/actuator/+/state",
    "farm/farm_001/zone/+/actuator/+/ack",
    "farm/farm_001/zone/+/actuator/+/command",
)


def _validator_for_topic(topic: str):
    parts = topic.split("/")

    if (
        len(parts) == 5
        and parts[0] == "farm"
        and parts[1]
        and parts[2] == "esp32"
        and parts[3]
        and parts[4] == "status"
    ):
        return validate_esp32_status, "ESP32 status"

    if (
        len(parts) == 7
        and parts[0] == "farm"
        and parts[1]
        and parts[2] == "zone"
        and parts[3]
        and parts[4] == "sensor"
        and parts[5]
        and parts[6] == "reading"
    ):
        return validate_sensor_reading, "sensor payload"

    if (
        len(parts) == 7
        and parts[0] == "farm"
        and parts[1]
        and parts[2] == "zone"
        and parts[3]
        and parts[4] == "actuator"
        and parts[5]
    ):
        validators = {
            "state": (validate_actuator_state, "actuator state"),
            "ack": (validate_actuator_ack, "actuator ack"),
            "command": (validate_actuator_command, "actuator command"),
        }
        return validators.get(parts[6])

    return None


def on_message(client, userdata, msg) -> None:
    validator_entry = _validator_for_topic(msg.topic)
    if validator_entry is None:
        print(f"MQTT unsupported topic: topic={msg.topic}")
        return

    validator, payload_name = validator_entry
    payload = parse_payload(msg.payload)

    if payload is None:
        print(f"MQTT invalid JSON: topic={msg.topic}")
        return

    if not validator(payload):
        print(f"MQTT invalid {payload_name}: topic={msg.topic}")
        return

    print(f"MQTT message received: topic={msg.topic} payload={payload}")


client.on_message = on_message


def connect() -> None:
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    for topic in TOPICS:
        client.subscribe(topic)
    client.loop_start()


def disconnect() -> None:
    client.loop_stop()
    client.disconnect()
