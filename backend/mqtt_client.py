import json

import paho.mqtt.client as mqtt

from mqtt_config import MQTT_HOST, MQTT_PASSWORD, MQTT_PORT, MQTT_USERNAME


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="smartfarm_backend",
)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)


def connect() -> None:
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)


def disconnect() -> None:
    client.disconnect()


def publish(topic: str, payload: dict) -> None:
    result = client.publish(topic, json.dumps(payload))
    result.wait_for_publish()
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(f"MQTT publish failed: rc={result.rc}")
