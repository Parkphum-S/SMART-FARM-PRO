import unittest

from mqtt_validator import validate_actuator_ack, validate_actuator_command, validate_actuator_state, validate_esp32_status, validate_sensor_reading


class TestSensorReadingValidation(unittest.TestCase):
    def setUp(self):
        self.valid_payload = {
            "sensor_id": "dht11_001",
            "type": "temperature_humidity",
            "temperature_c": 28.5,
            "humidity_pct": 72.0,
            "timestamp": "2026-10-08T00:00:00Z",
        }

    def test_valid_sensor_reading(self):
        self.assertTrue(validate_sensor_reading(self.valid_payload))

    def test_valid_temperature_humidity_soil_reading(self):
        payload = {
            **self.valid_payload,
            "sensor_id": "am2305b_001",
            "type": "temperature_humidity_soil",
            "soil_moisture_pct": 64.5,
        }
        self.assertTrue(validate_sensor_reading(payload))

    def test_soil_moisture_must_be_in_range(self):
        payload = {
            **self.valid_payload,
            "type": "temperature_humidity_soil",
            "soil_moisture_pct": 101,
        }
        self.assertFalse(validate_sensor_reading(payload))

    def test_soil_sensor_type_requires_soil_moisture(self):
        payload = {**self.valid_payload, "type": "temperature_humidity_soil"}
        self.assertFalse(validate_sensor_reading(payload))

    def test_missing_timestamp(self):
        payload = {key: value for key, value in self.valid_payload.items() if key != "timestamp"}
        self.assertFalse(validate_sensor_reading(payload))

    def test_wrong_type(self):
        payload = {**self.valid_payload, "type": "temperature"}
        self.assertFalse(validate_sensor_reading(payload))

    def test_invalid_timestamp(self):
        payload = {**self.valid_payload, "timestamp": "not-a-timestamp"}
        self.assertFalse(validate_sensor_reading(payload))


class TestEsp32StatusValidation(unittest.TestCase):
    def setUp(self):
        self.valid_payload = {
            "device_id": "esp32_001",
            "status": "online",
            "timestamp": "2026-10-08T00:00:00Z",
        }

    def test_valid_esp32_status(self):
        self.assertTrue(validate_esp32_status(self.valid_payload))

    def test_missing_timestamp(self):
        payload = {key: value for key, value in self.valid_payload.items() if key != "timestamp"}
        self.assertFalse(validate_esp32_status(payload))

    def test_invalid_status(self):
        payload = {**self.valid_payload, "status": "unknown"}
        self.assertFalse(validate_esp32_status(payload))

    def test_invalid_timestamp(self):
        payload = {**self.valid_payload, "timestamp": "not-a-timestamp"}
        self.assertFalse(validate_esp32_status(payload))


class TestActuatorStateValidation(unittest.TestCase):
    def setUp(self):
        self.valid_payload = {
            "actuator_id": "pump_001",
            "state": "on",
            "timestamp": "2026-10-08T00:00:00Z",
        }

    def test_valid_actuator_state(self):
        self.assertTrue(validate_actuator_state(self.valid_payload))

    def test_missing_timestamp(self):
        payload = {key: value for key, value in self.valid_payload.items() if key != "timestamp"}
        self.assertFalse(validate_actuator_state(payload))

    def test_invalid_state(self):
        payload = {**self.valid_payload, "state": "unknown"}
        self.assertFalse(validate_actuator_state(payload))

    def test_invalid_timestamp(self):
        payload = {**self.valid_payload, "timestamp": "not-a-timestamp"}
        self.assertFalse(validate_actuator_state(payload))


class TestActuatorAckValidation(unittest.TestCase):
    def setUp(self):
        self.valid_payload = {
            "actuator_id": "pump_001",
            "request_id": "req-001",
            "result": "accepted",
            "timestamp": "2026-10-08T00:00:00Z",
        }

    def test_valid_actuator_ack(self):
        self.assertTrue(validate_actuator_ack(self.valid_payload))

    def test_missing_request_id(self):
        payload = {key: value for key, value in self.valid_payload.items() if key != "request_id"}
        self.assertFalse(validate_actuator_ack(payload))

    def test_invalid_result(self):
        payload = {**self.valid_payload, "result": "unknown"}
        self.assertFalse(validate_actuator_ack(payload))

    def test_invalid_timestamp(self):
        payload = {**self.valid_payload, "timestamp": "not-a-timestamp"}
        self.assertFalse(validate_actuator_ack(payload))


class TestActuatorCommandValidation(unittest.TestCase):
    def setUp(self):
        self.valid_payload = {
            "actuator_id": "pump_001",
            "command": "on",
            "request_id": "req-001",
            "timestamp": "2026-10-08T00:00:00Z",
        }

    def test_valid_actuator_command(self):
        self.assertTrue(validate_actuator_command(self.valid_payload))

    def test_missing_request_id(self):
        payload = {key: value for key, value in self.valid_payload.items() if key != "request_id"}
        self.assertFalse(validate_actuator_command(payload))

    def test_invalid_command(self):
        payload = {**self.valid_payload, "command": "unknown"}
        self.assertFalse(validate_actuator_command(payload))

    def test_invalid_timestamp(self):
        payload = {**self.valid_payload, "timestamp": "not-a-timestamp"}
        self.assertFalse(validate_actuator_command(payload))


if __name__ == "__main__":
    unittest.main()
