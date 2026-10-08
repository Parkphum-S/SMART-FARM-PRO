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
