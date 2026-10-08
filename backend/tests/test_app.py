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
