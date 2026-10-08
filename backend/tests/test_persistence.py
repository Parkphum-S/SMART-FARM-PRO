import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, "backend")

import persistence


def test_insert_sensor_reading_returns_id():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    fake_cursor.fetchone.return_value = (42,)

    with patch("persistence.db.connect", return_value=fake_connection):
        result = persistence.insert_sensor_reading(
            sensor_id=7,
            recorded_at="2026-10-08T16:00:00+00:00",
            temperature_c=28.5,
            humidity_pct=72.0,
            value=None,
            raw_payload={"temperature": 28.5, "humidity": 72.0},
        )

    assert result == 42
    fake_cursor.execute.assert_called_once()

def test_resolve_sensor_id_returns_id():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    fake_cursor.fetchone.return_value = (42,)

    with patch("persistence.db.connect", return_value=fake_connection):
        result = persistence.resolve_sensor_id(
            farm_code="farm_001",
            zone_code="zone_01",
            sensor_code="dht11_001",
        )

    assert result == 42
    fake_cursor.execute.assert_called_once()


def test_resolve_sensor_id_returns_none_when_not_found():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    fake_cursor.fetchone.return_value = None

    with patch("persistence.db.connect", return_value=fake_connection):
        result = persistence.resolve_sensor_id(
            farm_code="farm_001",
            zone_code="zone_01",
            sensor_code="missing_sensor",
        )

    assert result is None
    fake_cursor.execute.assert_called_once()


def test_resolve_device_id_returns_id():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    fake_cursor.fetchone.return_value = (7,)

    with patch("persistence.db.connect", return_value=fake_connection):
        result = persistence.resolve_device_id(
            farm_code="farm_001",
            device_code="esp32_001",
        )

    assert result == 7
    fake_cursor.execute.assert_called_once()


def test_resolve_device_id_returns_none_when_not_found():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    fake_cursor.fetchone.return_value = None

    with patch("persistence.db.connect", return_value=fake_connection):
        result = persistence.resolve_device_id(
            farm_code="farm_001",
            device_code="missing_device",
        )

    assert result is None
    fake_cursor.execute.assert_called_once()


def test_update_device_status_updates_status_and_last_seen_at():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value

    with patch("persistence.db.connect", return_value=fake_connection):
        persistence.update_device_status(
            device_id=7,
            status="online",
            last_seen_at="2026-10-08T00:00:00Z",
        )

    fake_cursor.execute.assert_called_once_with(
        """
                UPDATE devices
                SET status = %s,
                    last_seen_at = %s
                WHERE id = %s
                """,
        ("online", "2026-10-08T00:00:00Z", 7),
    )

def test_resolve_actuator_id_returns_id():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    fake_cursor.fetchone.return_value = (11,)

    with patch("persistence.db.connect", return_value=fake_connection):
        result = persistence.resolve_actuator_id(
            farm_code="farm_001",
            zone_code="zone_01",
            actuator_code="pump_001",
        )

    assert result == 11
    fake_cursor.execute.assert_called_once()


def test_resolve_actuator_id_returns_none_when_not_found():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    fake_cursor.fetchone.return_value = None

    with patch("persistence.db.connect", return_value=fake_connection):
        result = persistence.resolve_actuator_id(
            farm_code="farm_001",
            zone_code="zone_01",
            actuator_code="missing_actuator",
        )

    assert result is None
    fake_cursor.execute.assert_called_once()

def test_insert_actuator_state_returns_id():
    fake_connection = MagicMock()
    fake_cursor = fake_connection.__enter__.return_value.cursor.return_value.__enter__.return_value
    fake_cursor.fetchone.return_value = (99,)

    with patch("persistence.db.connect", return_value=fake_connection):
        result = persistence.insert_actuator_state(
            actuator_id=11,
            state="on",
            recorded_at="2026-10-08T16:00:00+00:00",
            raw_payload={"actuator_id": "pump_001", "state": "on"},
        )

    assert result == 99
    fake_cursor.execute.assert_called_once()

def test_get_farm_settings():
    with patch("persistence.db.connect") as connect:
        cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (1, 13.7563, 100.5018, "auto")

        result = persistence.get_farm_settings(1)

    assert result == {
        "farm_id": 1,
        "latitude": 13.7563,
        "longitude": 100.5018,
        "location_source": "auto",
    }


def test_get_farm_settings_returns_none():
    with patch("persistence.db.connect") as connect:
        cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = None

        result = persistence.get_farm_settings(999)

    assert result is None


def test_upsert_farm_settings():
    with patch("persistence.db.connect") as connect:
        persistence.upsert_farm_settings(
            farm_id=1,
            latitude=13.7563,
            longitude=100.5018,
            location_source="auto",
        )

        cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        query = cursor.execute.call_args.args[0]
        params = cursor.execute.call_args.args[1]

    assert "ON CONFLICT (farm_id)" in query
    assert params == (1, 13.7563, 100.5018, "auto")


def test_get_user_for_auth_returns_active_user():
    with patch("persistence.db.connect") as connect:
        cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (
            7,
            "admin",
            "admin@example.com",
            "hashed-password",
            True,
        )

        result = persistence.get_user_for_auth("admin")

    assert result == {
        "id": 7,
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }
    cursor.execute.assert_called_once()


def test_get_user_for_auth_returns_none_when_not_found():
    with patch("persistence.db.connect") as connect:
        cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = None

        result = persistence.get_user_for_auth("missing-user")

    assert result is None
    cursor.execute.assert_called_once()
