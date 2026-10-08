import sys

sys.path.insert(0, "backend")

import mqtt_config


def test_default_mqtt_config():
    assert mqtt_config.MQTT_HOST == "localhost"
    assert mqtt_config.MQTT_PORT == 1883
    assert mqtt_config.MQTT_USERNAME == "smartfarm_backend"
    assert mqtt_config.MQTT_PASSWORD
