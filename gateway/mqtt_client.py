import paho.mqtt.client as mqtt

from mqtt_parser import parse_payload
from mqtt_validator import validate_payload
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

def on_message(client, userdata, msg) -> None:
    payload = parse_payload(msg.payload)
    if payload is None:
        print(f"MQTT invalid JSON: topic={msg.topic}")
        return
    if not validate_payload(payload):
        print(f"MQTT invalid payload: topic={msg.topic}")
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
