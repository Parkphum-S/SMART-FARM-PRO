import sys
from unittest.mock import patch

import dependencies
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
    from app import app

    user = {
        "id": 7,
        "username": "operator",
        "email": "operator@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }

    app.dependency_overrides = {
        dependencies.get_current_user: lambda: user,
    }

    try:
        with patch(
            "dependencies.persistence.get_user_permissions",
            return_value={"actuator.control"},
        ), patch("app.persistence.resolve_actuator_id", return_value=11), patch(
            "app.persistence.insert_actuator_command", return_value=123
        ), patch("app.mqtt_client.publish") as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-api-001",
                    "timestamp": "2026-10-08T00:00:00Z",
                },
            )

        assert response.status_code == 200
        assert response.json() == {
            "status": "accepted",
            "request_id": "req-api-001",
        }
        publish.assert_called_once_with(
            "farm/farm_001/zone/zone_01/actuator/pump_001/command",
            {
                "actuator_id": "pump_001",
                "command": "on",
                "request_id": "req-api-001",
                "timestamp": "2026-10-08T00:00:00Z",
            },
        )
    finally:
        app.dependency_overrides.clear()

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


def test_login_returns_access_token(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-only-secret-for-pytest-32-bytes-long")

    from app import app

    with patch(
        "persistence.get_user_for_auth",
        return_value={
            "id": 7,
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": "hashed-password",
            "is_active": True,
        },
    ), patch(
        "auth.verify_password",
        return_value=True,
    ), patch(
        "auth.create_access_token",
        return_value="test-access-token",
    ):
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "identifier": "admin",
                    "password": "correct-password",
                },
            )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-access-token",
        "token_type": "bearer",
    }


def test_login_rejects_invalid_credentials(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-only-secret-for-pytest-32-bytes-long")

    from app import app

    with patch(
        "persistence.get_user_for_auth",
        return_value=None,
    ):
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "identifier": "missing-user",
                    "password": "wrong-password",
                },
            )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_send_actuator_command_requires_authentication():
    from app import app

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/actuators/pump_001/command",
            json={
                "command": "on",
                "request_id": "req-api-002",
                "timestamp": "2026-10-09T00:00:00Z",
            },
        )

    assert response.status_code == 401


def test_send_actuator_command_requires_permission():
    from app import app

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }

    app.dependency_overrides = {
        dependencies.get_current_user: lambda: user,
    }

    try:
        with patch(
            "dependencies.persistence.get_user_permissions",
            return_value={"sensor.view"},
        ), TestClient(app) as client:
            response = client.post(
                "/api/v1/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-api-003",
                    "timestamp": "2026-10-09T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_send_actuator_command_allows_permission():
    from app import app

    user = {
        "id": 7,
        "username": "operator",
        "email": "operator@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }

    app.dependency_overrides = {
        dependencies.get_current_user: lambda: user,
    }

    try:
        with patch(
            "dependencies.persistence.get_user_permissions",
            return_value={"actuator.control"},
        ), patch("app.persistence.resolve_actuator_id", return_value=11), patch(
            "app.persistence.insert_actuator_command", return_value=123
        ), patch("app.mqtt_client.publish") as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-api-004",
                    "timestamp": "2026-10-09T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "accepted",
        "request_id": "req-api-004",
    }
    publish.assert_called_once()

def test_send_actuator_command_persists_before_publish():
    from app import app

    user = {
        "id": 7,
        "username": "operator",
        "email": "operator@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    events = []

    app.dependency_overrides = {
        dependencies.get_current_user: lambda: user,
    }

    try:
        with patch(
            "dependencies.persistence.get_user_permissions",
            return_value={"actuator.control"},
        ), patch(
            "persistence.resolve_actuator_id",
            return_value=11,
        ), patch(
            "persistence.insert_actuator_command",
            side_effect=lambda **kwargs: events.append(("persist", kwargs)) or 123,
        ), patch(
            "app.mqtt_client.publish",
            side_effect=lambda topic, payload: events.append(("publish", topic, payload)),
        ), TestClient(app) as client:
            response = client.post(
                "/api/v1/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-api-persist-001",
                    "timestamp": "2026-10-09T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert [event[0] for event in events] == ["persist", "publish"]
    assert events[0][1] == {
        "actuator_id": 11,
        "command": "on",
        "request_id": "req-api-persist-001",
        "requested_at": "2026-10-09T00:00:00Z",
        "raw_payload": {
            "actuator_id": "pump_001",
            "command": "on",
            "request_id": "req-api-persist-001",
            "timestamp": "2026-10-09T00:00:00Z",
        },
    }

def test_send_actuator_command_does_not_publish_when_persistence_fails():
    from app import app

    user = {
        "id": 7,
        "username": "operator",
        "email": "operator@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }

    app.dependency_overrides = {
        dependencies.get_current_user: lambda: user,
    }

    try:
        with patch(
            "dependencies.persistence.get_user_permissions",
            return_value={"actuator.control"},
        ), patch(
            "app.persistence.resolve_actuator_id",
            return_value=11,
        ), patch(
            "app.persistence.insert_actuator_command",
            side_effect=RuntimeError("database unavailable"),
        ), patch("app.mqtt_client.publish") as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-api-persist-fail-001",
                    "timestamp": "2026-10-09T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to record actuator command"}
    publish.assert_not_called()
