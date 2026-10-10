import json
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
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_device_id.return_value = 7

    messages = [
        MagicMock(topic="farm/farm_001/esp32/esp32_001/status", payload=b"{\"device_id\":\"esp32_001\",\"status\":\"online\",\"timestamp\":\"2026-10-08T00:00:00Z\"}"),
        MagicMock(topic="farm/farm_001/zone/zone_01/sensor/dht11_001/reading", payload=b"{\"sensor_id\":\"dht11_001\",\"type\":\"temperature_humidity\",\"temperature_c\":28.5,\"humidity_pct\":72.0,\"timestamp\":\"2026-10-08T00:00:00Z\"}"),
        MagicMock(topic="farm/farm_001/zone/zone_01/actuator/pump_001/state", payload=b"{\"actuator_id\":\"pump_001\",\"state\":\"on\",\"timestamp\":\"2026-10-08T00:00:00Z\"}"),
    ]

    for message in messages:
        mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.state_store.set_esp32_status.assert_called_once_with("esp32_001", {"device_id": "esp32_001", "status": "online", "timestamp": "2026-10-08T00:00:00Z", "farm_code": "farm_001"})
    mqtt_client.state_store.set_sensor_reading.assert_called_once_with("dht11_001", {"sensor_id": "dht11_001", "type": "temperature_humidity", "temperature_c": 28.5, "humidity_pct": 72.0, "timestamp": "2026-10-08T00:00:00Z", "farm_code": "farm_001", "zone_code": "zone_01"})
    mqtt_client.state_store.set_actuator_state.assert_called_once_with("pump_001", {"actuator_id": "pump_001", "state": "on", "timestamp": "2026-10-08T00:00:00Z", "farm_code": "farm_001", "zone_code": "zone_01"})

def test_on_sensor_message_persists_to_database_and_updates_state_store():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_sensor_id.return_value = 42

    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/sensor/dht11_001/reading",
        payload=b"{\"sensor_id\":\"dht11_001\",\"type\":\"temperature_humidity\",\"temperature_c\":28.5,\"humidity_pct\":72.0,\"timestamp\":\"2026-10-08T00:00:00Z\"}",
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_sensor_id.assert_called_once_with(
        "farm_001",
        "zone_01",
        "dht11_001",
    )
    mqtt_client.persistence.insert_sensor_reading.assert_called_once_with(
        sensor_id=42,
        recorded_at="2026-10-08T00:00:00Z",
        temperature_c=28.5,
        humidity_pct=72.0,
        value=None,
        raw_payload={
            "sensor_id": "dht11_001",
            "type": "temperature_humidity",
            "temperature_c": 28.5,
            "humidity_pct": 72.0,
            "timestamp": "2026-10-08T00:00:00Z",
        },
    )
    mqtt_client.state_store.set_sensor_reading.assert_called_once_with(
        "dht11_001",
        {
            "sensor_id": "dht11_001",
            "type": "temperature_humidity",
            "temperature_c": 28.5,
            "humidity_pct": 72.0,
            "timestamp": "2026-10-08T00:00:00Z",
            "farm_code": "farm_001",
            "zone_code": "zone_01",
        },
    )


def test_on_sensor_message_skips_database_when_sensor_cannot_be_resolved():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_sensor_id.return_value = None

    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/sensor/missing_sensor/reading",
        payload=b"{\"sensor_id\":\"missing_sensor\",\"type\":\"temperature_humidity\",\"temperature_c\":28.5,\"humidity_pct\":72.0,\"timestamp\":\"2026-10-08T00:00:00Z\"}",
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_sensor_id.assert_called_once_with(
        "farm_001",
        "zone_01",
        "missing_sensor",
    )
    mqtt_client.persistence.insert_sensor_reading.assert_not_called()
    mqtt_client.state_store.set_sensor_reading.assert_not_called()


def test_on_device_status_persists_to_database_and_updates_state_store():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_device_id.return_value = 7

    message = MagicMock(
        topic="farm/farm_001/esp32/esp32_001/status",
        payload=b"{\"device_id\":\"esp32_001\",\"status\":\"online\",\"timestamp\":\"2026-10-08T00:00:00Z\"}",
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_device_id.assert_called_once_with(
        "farm_001",
        "esp32_001",
    )
    mqtt_client.persistence.update_device_status.assert_called_once_with(
        device_id=7,
        status="online",
        last_seen_at="2026-10-08T00:00:00Z",
    )
    mqtt_client.state_store.set_esp32_status.assert_called_once_with(
        "esp32_001",
        {
            "device_id": "esp32_001",
            "status": "online",
            "timestamp": "2026-10-08T00:00:00Z",
            "farm_code": "farm_001",
        },
    )

def test_on_actuator_state_persists_to_database_and_updates_state_store():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_actuator_id.return_value = 11

    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/actuator/pump_001/state",
        payload=b"{\"actuator_id\":\"pump_001\",\"state\":\"on\",\"timestamp\":\"2026-10-08T00:00:00Z\"}",
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_actuator_id.assert_called_once_with(
        "farm_001",
        "zone_01",
        "pump_001",
    )
    mqtt_client.persistence.insert_actuator_state.assert_called_once_with(
        actuator_id=11,
        state="on",
        recorded_at="2026-10-08T00:00:00Z",
        raw_payload={
            "actuator_id": "pump_001",
            "state": "on",
            "timestamp": "2026-10-08T00:00:00Z",
        },
    )
    mqtt_client.state_store.set_actuator_state.assert_called_once_with(
        "pump_001",
        {
            "actuator_id": "pump_001",
            "state": "on",
            "timestamp": "2026-10-08T00:00:00Z",
            "farm_code": "farm_001",
            "zone_code": "zone_01",
        },
    )


def test_on_actuator_state_skips_database_when_actuator_cannot_be_resolved():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_actuator_id.return_value = None

    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/actuator/missing_actuator/state",
        payload=b"{\"actuator_id\":\"missing_actuator\",\"state\":\"off\",\"timestamp\":\"2026-10-08T00:00:00Z\"}",
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_actuator_id.assert_called_once_with(
        "farm_001",
        "zone_01",
        "missing_actuator",
    )
    mqtt_client.persistence.insert_actuator_state.assert_not_called()
    mqtt_client.state_store.set_actuator_state.assert_not_called()



def test_on_soil_sensor_message_persists_soil_moisture_value():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_sensor_id.return_value = 42

    payload = {
        "sensor_id": "am2305b_001",
        "type": "temperature_humidity_soil",
        "temperature_c": 28.5,
        "humidity_pct": 72.0,
        "soil_moisture_pct": 64.5,
        "timestamp": "2026-10-09T00:00:00Z",
    }
    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/sensor/am2305b_001/reading",
        payload=json.dumps(payload).encode("utf-8"),
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.insert_sensor_reading.assert_called_once_with(
        sensor_id=42,
        recorded_at="2026-10-09T00:00:00Z",
        temperature_c=28.5,
        humidity_pct=72.0,
        value=64.5,
        raw_payload=payload,
    )
    mqtt_client.state_store.set_sensor_reading.assert_called_once_with("am2305b_001", {**payload, "farm_code": "farm_001", "zone_code": "zone_01"})

def test_on_actuator_ack_persists_matching_command():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_actuator_id.return_value = 11

    payload = {
        "actuator_id": "pump_001",
        "request_id": "req-ack-001",
        "result": "accepted",
        "timestamp": "2026-10-09T10:00:00Z",
    }
    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/actuator/pump_001/ack",
        payload=json.dumps(payload).encode("utf-8"),
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_actuator_id.assert_called_once_with(
        "farm_001", "zone_01", "pump_001"
    )
    mqtt_client.persistence.update_actuator_command_ack.assert_called_once_with(
        actuator_id=11,
        request_id="req-ack-001",
        result="accepted",
        acknowledged_at="2026-10-09T10:00:00Z",
    )
    mqtt_client.state_store.set_actuator_state.assert_not_called()


def test_on_actuator_ack_rejects_payload_actuator_mismatch():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()

    payload = {
        "actuator_id": "pump_002",
        "request_id": "req-ack-002",
        "result": "accepted",
        "timestamp": "2026-10-09T10:00:00Z",
    }
    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/actuator/pump_001/ack",
        payload=json.dumps(payload).encode("utf-8"),
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_actuator_id.assert_not_called()
    mqtt_client.persistence.update_actuator_command_ack.assert_not_called()


def test_on_actuator_ack_rejects_invalid_result():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()

    payload = {
        "actuator_id": "pump_001",
        "request_id": "req-ack-003",
        "result": "unknown",
        "timestamp": "2026-10-09T10:00:00Z",
    }
    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/actuator/pump_001/ack",
        payload=json.dumps(payload).encode("utf-8"),
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_actuator_id.assert_not_called()
    mqtt_client.persistence.update_actuator_command_ack.assert_not_called()


def test_on_actuator_ack_skips_unknown_actuator():
    mqtt_client.state_store = MagicMock()
    mqtt_client.persistence = MagicMock()
    mqtt_client.persistence.resolve_actuator_id.return_value = None

    payload = {
        "actuator_id": "missing_actuator",
        "request_id": "req-ack-004",
        "result": "rejected",
        "timestamp": "2026-10-09T10:00:00Z",
    }
    message = MagicMock(
        topic="farm/farm_001/zone/zone_01/actuator/missing_actuator/ack",
        payload=json.dumps(payload).encode("utf-8"),
    )

    mqtt_client.on_message(mqtt_client.client, None, message)

    mqtt_client.persistence.resolve_actuator_id.assert_called_once_with(
        "farm_001", "zone_01", "missing_actuator"
    )
    mqtt_client.persistence.update_actuator_command_ack.assert_not_called()
