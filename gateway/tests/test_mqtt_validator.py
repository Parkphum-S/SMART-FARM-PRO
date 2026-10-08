import unittest

from mqtt_validator import validate_sensor_reading


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

    def test_missing_timestamp(self):
        payload = {key: value for key, value in self.valid_payload.items() if key != "timestamp"}
        self.assertFalse(validate_sensor_reading(payload))

    def test_wrong_type(self):
        payload = {**self.valid_payload, "type": "temperature"}
        self.assertFalse(validate_sensor_reading(payload))

    def test_invalid_timestamp(self):
        payload = {**self.valid_payload, "timestamp": "not-a-timestamp"}
        self.assertFalse(validate_sensor_reading(payload))


if __name__ == "__main__":
    unittest.main()
