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


@pytest.fixture(autouse=True)
def mock_mqtt_connection():
    with patch("app.mqtt_client.connect"), patch("app.mqtt_client.disconnect"):
        yield


@pytest.fixture(autouse=True)
def mock_actuator_farm_authorization():
    with patch(
        "app.persistence.user_can_access_actuator",
        return_value=True,
    ):
        yield



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
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"actuator.control"},
        ), patch("app.persistence.resolve_actuator_id", return_value=11), patch(
            "app.persistence.insert_actuator_command", return_value=123
        ), patch("app.mqtt_client.publish") as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
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

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    try:
        with patch(
            "dependencies.persistence.get_user_permissions",
            return_value={
                "device.view",
                "sensor.view",
                "actuator.view",
                "sensor.history",
            },
        ), patch(
            "app.persistence.list_user_farm_codes_with_permission",
            side_effect=lambda user_id, permission: {"farm_001"},
        ) as farm_permissions, patch(
            "app.state_store.get_esp32_status",
            return_value={
                "esp32_001": {
                    "status": "online",
                    "farm_code": "farm_001",
                },
                "esp32_002": {
                    "status": "online",
                    "farm_code": "farm_002",
                },
                "esp32_legacy": {"status": "online"},
            },
        ), patch(
            "app.state_store.get_sensor_readings",
            return_value={
                "dht11_001": {
                    "temperature_c": 28.5,
                    "farm_code": "farm_001",
                },
                "dht11_002": {
                    "temperature_c": 31.0,
                    "farm_code": "farm_002",
                },
                "dht11_legacy": {"temperature_c": 25.0},
            },
        ), patch(
            "app.state_store.get_actuator_states",
            return_value={
                "pump_001": {
                    "state": "on",
                    "farm_code": "farm_001",
                },
                "pump_002": {
                    "state": "off",
                    "farm_code": "farm_002",
                },
                "pump_legacy": {"state": "off"},
            },
        ), TestClient(app) as client:
            esp32_response = client.get("/api/v1/esp32/status")
            sensor_response = client.get("/api/v1/sensors/readings")
            actuator_response = client.get("/api/v1/actuators/states")

        assert [
            (call.kwargs["user_id"], call.kwargs["permission"])
            for call in farm_permissions.call_args_list
        ] == [
            (7, "device.view"),
            (7, "sensor.view"),
            (7, "actuator.view"),
        ]

        assert esp32_response.status_code == 200
        assert esp32_response.json()["data"] == {
            "esp32_001": {
                "status": "online",
                "farm_code": "farm_001",
            }
        }
        assert sensor_response.status_code == 200
        assert sensor_response.json()["data"] == {
            "dht11_001": {
                "temperature_c": 28.5,
                "farm_code": "farm_001",
            }
        }
        assert actuator_response.status_code == 200
        assert actuator_response.json()["data"] == {
            "pump_001": {
                "state": "on",
                "farm_code": "farm_001",
            }
        }
    finally:
        app.dependency_overrides.clear()


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
            "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
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
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"sensor.view"},
        ), TestClient(app) as client:
            response = client.post(
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
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
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"actuator.control"},
        ), patch("app.persistence.resolve_actuator_id", return_value=11), patch(
            "app.persistence.insert_actuator_command", return_value=123
        ), patch("app.mqtt_client.publish") as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
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
            "dependencies.persistence.get_farm_user_permissions",
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
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
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
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"actuator.control"},
        ), patch(
            "app.persistence.resolve_actuator_id",
            return_value=11,
        ), patch(
            "app.persistence.insert_actuator_command",
            side_effect=RuntimeError("database unavailable"),
        ), patch("app.mqtt_client.publish") as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
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

def test_send_actuator_command_returns_error_when_mqtt_publish_fails():
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
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"actuator.control"},
        ), patch(
            "app.persistence.resolve_actuator_id",
            return_value=11,
        ), patch(
            "app.persistence.insert_actuator_command",
            return_value=124,
        ) as persist, patch(
            "app.mqtt_client.publish",
            side_effect=RuntimeError("MQTT unavailable"),
        ) as publish, TestClient(app, raise_server_exceptions=False) as client:
            response = client.post(
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-api-mqtt-fail-001",
                    "timestamp": "2026-10-09T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Failed to publish actuator command"
    }
    persist.assert_called_once()
    publish.assert_called_once()


def test_get_sensor_reading_history_uses_persistence_filters():
    from app import app

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    rows = [
        {
            "id": 55,
            "farm_code": "farm_001",
            "zone_code": "zone_01",
            "sensor_code": "am2305b_001",
            "recorded_at": "2026-10-09T12:00:00+00:00",
            "temperature_c": 29.1,
            "humidity_pct": 68.0,
            "value": 64.5,
            "raw_payload": {"soil_moisture_pct": 64.5},
        }
    ]

    try:
        with patch(
            "app.persistence.list_user_farm_codes_with_permission",
            return_value={"farm_001"},
        ) as farm_permissions, patch(
            "app.persistence.list_sensor_readings",
            return_value=rows,
        ) as list_readings, TestClient(app) as client:
            response = client.get(
                "/api/v1/sensors/readings/history",
                params={
                    "limit": 25,
                    "sensor_code": "am2305b_001",
                    "farm_code": "farm_001",
                    "zone_code": "zone_01",
                },
            )

        assert response.status_code == 200
        assert response.json() == {"data": rows}
        farm_permissions.assert_called_once_with(
            user_id=7,
            permission="sensor.history",
        )
        list_readings.assert_called_once_with(
            user_id=7,
            authorized_farm_codes={"farm_001"},
            limit=25,
            sensor_code="am2305b_001",
            farm_code="farm_001",
            zone_code="zone_01",
        )
    finally:
        app.dependency_overrides.clear()


def test_sensor_history_denies_farm_outside_authorized_set():
    from app import app

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    try:
        with patch(
            "app.persistence.list_user_farm_codes_with_permission",
            return_value={"farm_001"},
        ), patch("app.persistence.list_sensor_readings") as list_readings, TestClient(app) as client:
            response = client.get(
                "/api/v1/sensors/readings/history",
                params={"farm_code": "farm_999"},
            )

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}
        list_readings.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_sensor_history_fails_closed_when_farm_authorization_unavailable():
    from app import app

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    try:
        with patch(
            "app.persistence.list_user_farm_codes_with_permission",
            side_effect=RuntimeError("database unavailable"),
        ), patch("app.persistence.list_sensor_readings") as list_readings, TestClient(app) as client:
            response = client.get("/api/v1/sensors/readings/history")

        assert response.status_code == 503
        assert response.json() == {
            "detail": "Farm authorization service unavailable"
        }
        list_readings.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_sensor_history_without_farm_filter_uses_all_authorized_farms():
    from app import app

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    try:
        with patch(
            "app.persistence.list_user_farm_codes_with_permission",
            return_value={"farm_001", "farm_002"},
        ), patch(
            "app.persistence.list_sensor_readings",
            return_value=[],
        ) as list_readings, TestClient(app) as client:
            response = client.get("/api/v1/sensors/readings/history")

        assert response.status_code == 200
        list_readings.assert_called_once_with(
            user_id=7,
            authorized_farm_codes={"farm_001", "farm_002"},
            limit=100,
            sensor_code=None,
            farm_code=None,
            zone_code=None,
        )
    finally:
        app.dependency_overrides.clear()


def test_get_sensor_reading_history_validates_limit():
    from app import app

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    try:
        with patch(
            "app.persistence.list_user_farm_codes_with_permission",
        ) as farm_permissions, patch(
            "app.persistence.list_sensor_readings",
        ) as list_readings, TestClient(app) as client:
            response = client.get(
                "/api/v1/sensors/readings/history",
                params={"limit": 0},
            )

        assert response.status_code == 422
        farm_permissions.assert_not_called()
        list_readings.assert_not_called()
    finally:
        app.dependency_overrides.clear()




@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/esp32/status",
        "/api/v1/sensors/readings",
        "/api/v1/actuators/states",
    ],
)
def test_live_state_fails_closed_when_farm_authorization_unavailable(endpoint):
    from app import app

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    try:
        with patch(
            "dependencies.persistence.get_user_permissions",
            return_value={
                "device.view",
                "sensor.view",
                "actuator.view",
            },
        ), patch(
            "app.persistence.list_user_farm_codes_with_permission",
            side_effect=RuntimeError("database unavailable"),
        ), TestClient(app) as client:
            response = client.get(endpoint)

        assert response.status_code == 503
        assert response.json() == {
            "detail": "Farm authorization service unavailable"
        }
    finally:
        app.dependency_overrides.clear()


READ_ENDPOINTS = [
    "/api/v1/esp32/status",
    "/api/v1/sensors/readings",
    "/api/v1/sensors/readings/history",
    "/api/v1/actuators/states",
]


@pytest.mark.parametrize("endpoint", READ_ENDPOINTS)
def test_read_endpoints_require_authentication(endpoint):
    from app import app

    app.dependency_overrides.clear()
    try:
        with TestClient(app) as client:
            response = client.get(endpoint)

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("endpoint", READ_ENDPOINTS)
def test_read_endpoints_reject_user_without_permission(endpoint):
    from app import app

    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    try:
        with patch(
            "dependencies.persistence.get_user_permissions",
            return_value=set(),
        ), patch(
            "app.persistence.list_user_farm_codes_with_permission",
            return_value=set(),
        ), TestClient(app) as client:
            response = client.get(endpoint)

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}
    finally:
        app.dependency_overrides.clear()


def test_send_actuator_command_denies_non_member():
    from app import app

    user = {
        "id": 8,
        "username": "other_farm_operator",
        "email": "operator@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }

    app.dependency_overrides = {
        dependencies.get_current_user: lambda: user,
    }

    try:
        with patch(
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"actuator.control"},
        ), patch(
            "app.persistence.resolve_actuator_id",
            return_value=11,
        ), patch(
            "app.persistence.user_can_access_actuator",
            return_value=False,
        ) as access_check, patch(
            "app.persistence.insert_actuator_command",
        ) as persist, patch(
            "app.mqtt_client.publish",
        ) as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-api-non-member-001",
                    "timestamp": "2026-10-10T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
    access_check.assert_called_once_with(user_id=8, actuator_id=11)
    persist.assert_not_called()
    publish.assert_not_called()


def test_send_actuator_command_fails_closed_when_resolution_fails():
    from app import app

    user = {
        "id": 8,
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
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"actuator.control"},
        ), patch(
            "app.persistence.resolve_actuator_id",
            side_effect=RuntimeError("database unavailable"),
        ), patch(
            "app.persistence.user_can_access_actuator",
        ) as access_check, patch(
            "app.persistence.insert_actuator_command",
        ) as persist, patch(
            "app.mqtt_client.publish",
        ) as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-resolution-error-001",
                    "timestamp": "2026-10-10T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    access_check.assert_not_called()
    persist.assert_not_called()
    publish.assert_not_called()


def test_send_actuator_command_fails_closed_when_access_check_fails():
    from app import app

    user = {
        "id": 8,
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
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"actuator.control"},
        ), patch(
            "app.persistence.resolve_actuator_id",
            return_value=11,
        ) as resolve_actuator, patch(
            "app.persistence.user_can_access_actuator",
            side_effect=RuntimeError("database unavailable"),
        ) as access_check, patch(
            "app.persistence.insert_actuator_command",
        ) as persist, patch(
            "app.mqtt_client.publish",
        ) as publish, TestClient(app) as client:
            response = client.post(
                "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
                json={
                    "command": "on",
                    "request_id": "req-access-error-001",
                    "timestamp": "2026-10-10T00:00:00Z",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    resolve_actuator.assert_called_once_with(
        "farm_001",
        "zone_01",
        "pump_001",
    )
    access_check.assert_called_once_with(user_id=8, actuator_id=11)
    persist.assert_not_called()
    publish.assert_not_called()

def test_send_actuator_command_rejects_invalid_payloads():
    from fastapi.testclient import TestClient
    from unittest.mock import patch
    import dependencies
    from app import app

    user = {
        "id": 7,
        "username": "operator",
        "email": "operator@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    app.dependency_overrides[dependencies.get_current_user] = lambda: user

    invalid_payloads = [
        {
            "command": "restart",
            "request_id": "req-invalid-command",
            "timestamp": "2026-10-08T00:00:00Z",
        },
        {
            "command": "on",
            "request_id": "   ",
            "timestamp": "2026-10-08T00:00:00Z",
        },
        {
            "command": "on",
            "request_id": "req-naive-timestamp",
            "timestamp": "2026-10-08T00:00:00",
        },
    ]

    try:
        with patch(
            "dependencies.persistence.get_farm_user_permissions",
            return_value={"actuator.control"},
        ), patch(
            "app.persistence.resolve_actuator_id",
            return_value=11,
        ), patch(
            "app.persistence.insert_actuator_command",
        ) as persist, patch(
            "app.mqtt_client.publish",
        ) as publish, TestClient(app) as client:
            for payload in invalid_payloads:
                response = client.post(
                    "/api/v1/farms/farm_001/zones/zone_01/actuators/pump_001/command",
                    json=payload,
                )
                assert response.status_code == 422, (
                    f"Expected 422 for payload {payload!r}, "
                    f"got {response.status_code}: {response.text}"
                )

            persist.assert_not_called()
            publish.assert_not_called()
    finally:
        app.dependency_overrides.pop(dependencies.get_current_user, None)
