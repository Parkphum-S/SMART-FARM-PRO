import paho.mqtt.client as mqtt

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


def connect() -> None:
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()


def disconnect() -> None:
    client.loop_stop()
    client.disconnect()
