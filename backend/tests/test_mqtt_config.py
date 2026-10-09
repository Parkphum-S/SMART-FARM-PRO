import importlib
import sys

import pytest

sys.path.insert(0, "backend")

import mqtt_config


def test_default_mqtt_config(monkeypatch):
    for key in (
        "MQTT_HOST",
        "MQTT_PORT",
        "MQTT_BACKEND_USERNAME",
        "MQTT_BACKEND_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)

    config = importlib.reload(mqtt_config)
    assert config.MQTT_HOST == "localhost"
    assert config.MQTT_PORT == 1883
    assert config.MQTT_USERNAME == "smartfarm_backend"
    assert config.MQTT_PASSWORD == ""
