import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, "backend")

from app import lifespan


@pytest.mark.asyncio
async def test_lifespan_manages_mqtt_client():
    app = object()
    with patch("app.mqtt_client.connect") as connect, patch("app.mqtt_client.disconnect") as disconnect:
        async with lifespan(app):
            connect.assert_called_once()
            disconnect.assert_not_called()
        disconnect.assert_called_once()

from fastapi.testclient import TestClient


def test_send_actuator_command():
    with patch("app.mqtt_client.publish") as publish:
        from app import app
        with TestClient(app) as client:
            response = client.post("/api/v1/actuators/pump_001/command", json={"command": "on", "request_id": "req-api-001", "timestamp": "2026-10-08T00:00:00Z"})
        assert response.status_code == 200
        assert response.json() == {"status": "accepted", "request_id": "req-api-001"}
        publish.assert_called_once_with("farm/farm_001/zone/zone_01/actuator/pump_001/command", {"actuator_id": "pump_001", "command": "on", "request_id": "req-api-001", "timestamp": "2026-10-08T00:00:00Z"})

def test_get_latest_farm_data():
    from app import app
    with patch("app.state_store.get_esp32_status", return_value={"esp32_001": {"status": "online"}}), patch("app.state_store.get_sensor_readings", return_value={"dht11_001": {"temperature_c": 28.5}}), patch("app.state_store.get_actuator_states", return_value={"pump_001": {"state": "on"}}):
        with TestClient(app) as client:
            esp32_response = client.get("/api/v1/esp32/status")
            sensor_response = client.get("/api/v1/sensors/readings")
            actuator_response = client.get("/api/v1/actuators/states")

    assert esp32_response.status_code == 200
    assert esp32_response.json() == {"data": {"esp32_001": {"status": "online"}}}
    assert sensor_response.status_code == 200
    assert sensor_response.json() == {"data": {"dht11_001": {"temperature_c": 28.5}}}
    assert actuator_response.status_code == 200
    assert actuator_response.json() == {"data": {"pump_001": {"state": "on"}}}
