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
