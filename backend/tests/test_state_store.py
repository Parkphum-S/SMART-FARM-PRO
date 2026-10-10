import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import state_store


@pytest.fixture(autouse=True)
def clear_state_store():
    state_store._esp32_status.clear()
    state_store._sensor_readings.clear()
    state_store._actuator_states.clear()
    yield
    state_store._esp32_status.clear()
    state_store._sensor_readings.clear()
    state_store._actuator_states.clear()


def test_esp32_status_is_isolated_by_farm():
    state_store.set_esp32_status(
        "esp32_001",
        {"farm_code": "farm_001", "status": "online"},
    )
    state_store.set_esp32_status(
        "esp32_001",
        {"farm_code": "farm_002", "status": "offline"},
    )

    assert len(state_store.get_esp32_status()) == 2


def test_sensor_readings_are_isolated_by_farm_and_zone():
    state_store.set_sensor_reading(
        "dht11_001",
        {
            "farm_code": "farm_001",
            "zone_code": "zone_01",
            "temperature_c": 28.5,
        },
    )
    state_store.set_sensor_reading(
        "dht11_001",
        {
            "farm_code": "farm_002",
            "zone_code": "zone_01",
            "temperature_c": 31.0,
        },
    )

    assert len(state_store.get_sensor_readings()) == 2


def test_actuator_states_are_isolated_by_farm_and_zone():
    state_store.set_actuator_state(
        "pump_001",
        {
            "farm_code": "farm_001",
            "zone_code": "zone_01",
            "state": "on",
        },
    )
    state_store.set_actuator_state(
        "pump_001",
        {
            "farm_code": "farm_002",
            "zone_code": "zone_01",
            "state": "off",
        },
    )

    assert len(state_store.get_actuator_states()) == 2
