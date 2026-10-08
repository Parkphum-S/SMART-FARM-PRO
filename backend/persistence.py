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
