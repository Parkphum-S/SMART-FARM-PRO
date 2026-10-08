from typing import Any

import db
from psycopg.types.json import Jsonb


def insert_sensor_reading(
    sensor_id: int,
    recorded_at: str,
    temperature_c: float | None = None,
    humidity_pct: float | None = None,
    value: float | None = None,
    raw_payload: dict[str, Any] | None = None,
) -> int:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sensor_readings (
                    sensor_id,
                    recorded_at,
                    temperature_c,
                    humidity_pct,
                    value,
                    raw_payload
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    sensor_id,
                    recorded_at,
                    temperature_c,
                    humidity_pct,
                    value,
                    Jsonb(raw_payload) if raw_payload is not None else None,
                ),
            )
            row = cur.fetchone()

    return row[0]

def update_device_status(
    device_id: int,
    status: str,
    last_seen_at: str | None = None,
) -> None:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE devices
                SET status = %s,
                    last_seen_at = %s
                WHERE id = %s
                """,
                (status, last_seen_at, device_id),
            )

def resolve_device_id(
    farm_code: str,
    device_code: str,
) -> int | None:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.id
                FROM devices AS d
                JOIN farms AS f ON f.id = d.farm_id
                WHERE f.farm_code = %s
                  AND d.device_code = %s
                """,
                (farm_code, device_code),
            )
            row = cur.fetchone()

    return row[0] if row else None

def insert_actuator_state(
    actuator_id: int,
    state: str,
    recorded_at: str,
    raw_payload: dict[str, Any] | None = None,
) -> int:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO actuator_states (
                    actuator_id,
                    state,
                    recorded_at,
                    raw_payload
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    actuator_id,
                    state,
                    recorded_at,
                    Jsonb(raw_payload) if raw_payload is not None else None,
                ),
            )
            row = cur.fetchone()

    return row[0]


def resolve_actuator_id(
    farm_code: str,
    zone_code: str,
    actuator_code: str,
) -> int | None:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.id
                FROM actuators AS a
                JOIN farms AS f ON f.id = a.farm_id
                JOIN zones AS z ON z.id = a.zone_id
                WHERE f.farm_code = %s
                  AND z.zone_code = %s
                  AND a.actuator_code = %s
                """,
                (farm_code, zone_code, actuator_code),
            )
            row = cur.fetchone()

    return row[0] if row else None


def resolve_sensor_id(
    farm_code: str,
    zone_code: str,
    sensor_code: str,
) -> int | None:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id
                FROM sensors AS s
                JOIN farms AS f ON f.id = s.farm_id
                JOIN zones AS z ON z.id = s.zone_id
                WHERE f.farm_code = %s
                  AND z.zone_code = %s
                  AND s.sensor_code = %s
                """,
                (farm_code, zone_code, sensor_code),
            )
            row = cur.fetchone()

    return row[0] if row else None
