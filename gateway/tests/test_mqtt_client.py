import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace

import mqtt_client


class TestGatewayMqttClient(unittest.TestCase):
    def make_message(self, topic, payload):
        return SimpleNamespace(
            topic=topic,
            payload=json.dumps(payload).encode("utf-8"),
        )

    def run_message(self, topic, payload):
        output = StringIO()
        message = SimpleNamespace(topic=topic, payload=payload)
        with redirect_stdout(output):
            mqtt_client.on_message(None, None, message)
        return output.getvalue()

    def test_valid_sensor_reading_is_received(self):
        payload = {
            "sensor_id": "dht11_001",
            "type": "temperature_humidity",
            "temperature_c": 28.5,
            "humidity_pct": 72.0,
            "timestamp": "2026-10-08T00:00:00Z",
        }
        output = self.run_message(
            "farm/farm_001/zone/zone_01/sensor/dht11_001/reading",
            json.dumps(payload).encode(),
        )
        self.assertIn("MQTT message received", output)

    def test_valid_esp32_status_is_received(self):
        payload = {
            "device_id": "esp32_001",
            "status": "online",
            "timestamp": "2026-10-08T00:00:00Z",
        }
        output = self.run_message(
            "farm/farm_001/esp32/esp32_001/status",
            json.dumps(payload).encode(),
        )
        self.assertIn("MQTT message received", output)

    def test_invalid_esp32_status_is_rejected(self):
        output = self.run_message(
            "farm/farm_001/esp32/esp32_001/status",
            b'{"status":"online"}',
        )
        self.assertIn("MQTT invalid", output)
        self.assertNotIn("MQTT message received", output)

    def test_valid_actuator_state_is_received(self):
        payload = {
            "actuator_id": "pump_001",
            "state": "on",
            "timestamp": "2026-10-08T00:00:00Z",
        }
        output = self.run_message(
            "farm/farm_001/zone/zone_01/actuator/pump_001/state",
            json.dumps(payload).encode(),
        )
        self.assertIn("MQTT message received", output)

    def test_invalid_actuator_state_is_rejected(self):
        output = self.run_message(
            "farm/farm_001/zone/zone_01/actuator/pump_001/state",
            b'{"actuator_id":"pump_001","state":"unknown"}',
        )
        self.assertIn("MQTT invalid", output)
        self.assertNotIn("MQTT message received", output)

    def test_valid_actuator_ack_is_received(self):
        payload = {
            "actuator_id": "pump_001",
            "request_id": "req-001",
            "result": "accepted",
            "timestamp": "2026-10-08T00:00:00Z",
        }
        output = self.run_message(
            "farm/farm_001/zone/zone_01/actuator/pump_001/ack",
            json.dumps(payload).encode(),
        )
        self.assertIn("MQTT message received", output)

    def test_valid_actuator_command_is_received(self):
        payload = {
            "actuator_id": "pump_001",
            "command": "on",
            "request_id": "req-001",
            "timestamp": "2026-10-08T00:00:00Z",
        }
        output = self.run_message(
            "farm/farm_001/zone/zone_01/actuator/pump_001/command",
            json.dumps(payload).encode(),
        )
        self.assertIn("MQTT message received", output)

    def test_invalid_json_is_rejected(self):
        output = self.run_message(
            "farm/farm_001/esp32/esp32_001/status",
            b"{invalid-json",
        )
        self.assertIn("MQTT invalid JSON", output)
        self.assertNotIn("MQTT message received", output)

    def test_unknown_topic_is_rejected(self):
        output = self.run_message(
            "unrecognized/topic",
            b'{"status":"online"}',
        )
        self.assertIn("MQTT unsupported topic", output)
        self.assertNotIn("MQTT message received", output)


if __name__ == "__main__":
    unittest.main()
