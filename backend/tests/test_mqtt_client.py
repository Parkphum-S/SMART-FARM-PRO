import sys
from unittest.mock import MagicMock

sys.path.insert(0, "backend")

import mqtt_client


def test_publish_serializes_payload_and_publishes():
    mock_result = MagicMock()
    mock_result.rc = 0
    mqtt_client.client = MagicMock()
    mqtt_client.client.publish.return_value = mock_result

    payload = {"actuator_id": "pump_001", "command": "on", "request_id": "req-test-001", "timestamp": "2026-10-08T00:00:00Z"}

    mqtt_client.publish("farm/farm_001/zone/zone_01/actuator/pump_001/command", payload)

    mqtt_client.client.publish.assert_called_once()
    topic, message = mqtt_client.client.publish.call_args.args
    assert topic == "farm/farm_001/zone/zone_01/actuator/pump_001/command"
    assert message == "{\"actuator_id\": \"pump_001\", \"command\": \"on\", \"request_id\": \"req-test-001\", \"timestamp\": \"2026-10-08T00:00:00Z\"}"
    mock_result.wait_for_publish.assert_called_once()

def test_on_message_updates_state_store():
    mqtt_client.state_store = MagicMock()

    messages = [
        MagicMock(topic="farm/farm_001/esp32/esp32_001/status", payload=b"{\"device_id\":\"esp32_001\",\"status\":\"online\",\"timestamp\":\"2026-10-08T00:00:00Z\"}"),
        MagicMock(topic="farm/farm_001/zone/zone_01/sensor/dht11_001/reading", payload=b"{\"sensor_id\":\"dht11_001\",\"type\":\"temperature_humidity\",\"temperature_c\":28.5,\"humidity_pct\":72.0,\"timestamp\":\"2026-10-08T00:00:00Z\"}"),
        MagicMock(topic="farm/farm_001/zone/zone_01/actuator/pump_001/state", payload=b"{\"actuator_id\":\"pump_001\",\"state\":\"on\",\"timestamp\":\"2026-10-08T00:00:00Z\"}"),
    ]

    for message in messages:
        mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.state_store.set_esp32_status.assert_called_once_with("esp32_001", {"device_id": "esp32_001", "status": "online", "timestamp": "2026-10-08T00:00:00Z"})
    mqtt_client.state_store.set_sensor_reading.assert_called_once_with("dht11_001", {"sensor_id": "dht11_001", "type": "temperature_humidity", "temperature_c": 28.5, "humidity_pct": 72.0, "timestamp": "2026-10-08T00:00:00Z"})
    mqtt_client.state_store.set_actuator_state.assert_called_once_with("pump_001", {"actuator_id": "pump_001", "state": "on", "timestamp": "2026-10-08T00:00:00Z"})
