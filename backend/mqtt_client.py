import json

import paho.mqtt.client as mqtt

from mqtt_config import MQTT_HOST, MQTT_PASSWORD, MQTT_PORT, MQTT_USERNAME
import state_store
import persistence


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="smartfarm_backend",
)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)


def on_message(client, userdata, msg) -> None:
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return
    parts = msg.topic.split("/")
    if len(parts) == 5 and parts[2] == "esp32" and parts[4] == "status":
        device_id = payload.get("device_id") or payload.get("esp32_id")
        if device_id:
            farm_code = parts[1]
            resolved_device_id = persistence.resolve_device_id(
                farm_code,
                device_id,
            )
            if resolved_device_id is not None:
                persistence.update_device_status(
                    device_id=resolved_device_id,
                    status=payload.get("status", "unknown"),
                    last_seen_at=payload.get("timestamp"),
                )
            state_store.set_esp32_status(device_id, payload)
    elif len(parts) == 7 and parts[2] == "zone" and parts[4] == "sensor" and parts[6] == "reading":
        sensor_id = payload.get("sensor_id")
        if sensor_id:
            farm_code = parts[1]
            zone_code = parts[3]
            resolved_sensor_id = persistence.resolve_sensor_id(
                farm_code,
                zone_code,
                sensor_id,
            )

            if resolved_sensor_id is not None:
                persistence.insert_sensor_reading(
                    sensor_id=resolved_sensor_id,
                    recorded_at=payload.get("timestamp"),
                    temperature_c=payload.get("temperature_c"),
                    humidity_pct=payload.get("humidity_pct"),
                    value=payload.get("value"),
                    raw_payload=payload,
                )

            state_store.set_sensor_reading(sensor_id, payload)
    elif len(parts) == 7 and parts[2] == "zone" and parts[4] == "actuator" and parts[6] == "state":
        actuator_id = payload.get("actuator_id")
        if actuator_id:
            farm_code = parts[1]
            zone_code = parts[3]
            resolved_actuator_id = persistence.resolve_actuator_id(
                farm_code,
                zone_code,
                actuator_id,
            )

            if resolved_actuator_id is not None:
                persistence.insert_actuator_state(
                    actuator_id=resolved_actuator_id,
                    state=payload.get("state", "unknown"),
                    recorded_at=payload.get("timestamp"),
                    raw_payload=payload,
                )

            state_store.set_actuator_state(actuator_id, payload)

client.on_message = on_message

TOPICS = (
    "farm/farm_001/esp32/+/status",
    "farm/farm_001/zone/+/sensor/+/reading",
    "farm/farm_001/zone/+/actuator/+/state",
)

def connect() -> None:
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    for topic in TOPICS:
        client.subscribe(topic)
    client.loop_start()


def disconnect() -> None:
    client.loop_stop()
    client.disconnect()


def publish(topic: str, payload: dict) -> None:
    result = client.publish(topic, json.dumps(payload))
    result.wait_for_publish()
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError(f"MQTT publish failed: rc={result.rc}")
