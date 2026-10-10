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

def insert_actuator_command(
    actuator_id: int,
    command: str,
    request_id: str,
    requested_at: str,
    raw_payload: dict[str, Any] | None = None,
) -> int:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO actuator_commands (
                    actuator_id,
                    command,
                    request_id,
                    requested_at,
                    raw_payload
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    actuator_id,
                    command,
                    request_id,
                    requested_at,
                    Jsonb(raw_payload) if raw_payload is not None else None,
                ),
            )
            row = cur.fetchone()

    return row[0]


def update_actuator_command_ack(
    actuator_id: int,
    request_id: str,
    result: str,
    acknowledged_at: str,
) -> bool:
    if result not in {"accepted", "rejected"}:
        return False

    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE actuator_commands
                SET acknowledged_at = %s,
                    result = %s
                WHERE request_id = %s
                  AND actuator_id = %s
                  AND acknowledged_at IS NULL
                RETURNING id
                """,
                (
                    acknowledged_at,
                    result,
                    request_id,
                    actuator_id,
                ),
            )
            row = cur.fetchone()

    return row is not None


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
                JOIN zones AS z ON z.id = a.zone_id AND z.farm_id = a.farm_id
                WHERE f.farm_code = %s
                  AND z.zone_code = %s
                  AND a.actuator_code = %s
                """,
                (farm_code, zone_code, actuator_code),
            )
            row = cur.fetchone()

    return row[0] if row else None



def user_can_access_actuator(user_id: int, actuator_id: int) -> bool:
    """Return whether the user belongs to the farm owning this actuator."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM actuators AS a
                    JOIN farm_users AS fu ON fu.farm_id = a.farm_id
                    WHERE a.id = %s
                      AND fu.user_id = %s
                )
                """,
                (actuator_id, user_id),
            )
            row = cur.fetchone()

    return bool(row and row[0])

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
                JOIN zones AS z ON z.id = s.zone_id AND z.farm_id = s.farm_id
                WHERE f.farm_code = %s
                  AND z.zone_code = %s
                  AND s.sensor_code = %s
                """,
                (farm_code, zone_code, sensor_code),
            )
            row = cur.fetchone()

    return row[0] if row else None

def get_user_by_id(user_id: int) -> dict[str, object] | None:
    """Return an active user by primary key for access-token validation."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, email, password_hash, is_active
                FROM users
                WHERE id = %s AND is_active = true
                """,
                (user_id,),
            )
            row = cur.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "password_hash": row[3],
        "is_active": row[4],
    }


def get_user_for_auth(identifier: str) -> dict[str, object] | None:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, email, password_hash, is_active
                FROM users
                WHERE is_active = true
                  AND (username = %s OR email = %s)
                """,
                (identifier, identifier),
            )
            row = cur.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "password_hash": row[3],
        "is_active": row[4],
    }



def get_user_permissions(user_id: int) -> set[str]:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT p.name
                FROM user_roles AS ur
                JOIN role_permissions AS rp ON rp.role_id = ur.role_id
                JOIN permissions AS p ON p.id = rp.permission_id
                WHERE ur.user_id = %s
                """,
                (user_id,),
            )
            rows = cur.fetchall()

    return {row[0] for row in rows}


def list_user_farm_codes(user_id: int) -> set[str]:
    """Return farm codes assigned to a user through farm membership."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT f.farm_code
                FROM farm_users AS fu
                JOIN farms AS f ON f.id = fu.farm_id
                WHERE fu.user_id = %s
                ORDER BY f.farm_code
                """,
                (user_id,),
            )
            rows = cur.fetchall()

    return {row[0] for row in rows if row[0]}


def get_farm_settings(
    farm_id: int,
) -> dict[str, object] | None:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT farm_id, latitude, longitude, location_source
                FROM farm_settings
                WHERE farm_id = %s
                """,
                (farm_id,),
            )
            row = cur.fetchone()

    if row is None:
        return None

    return {
        "farm_id": row[0],
        "latitude": row[1],
        "longitude": row[2],
        "location_source": row[3],
    }


def upsert_farm_settings(
    farm_id: int,
    latitude: float | None,
    longitude: float | None,
    location_source: str = "auto",
) -> None:
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO farm_settings (
                    farm_id,
                    latitude,
                    longitude,
                    location_source,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (farm_id)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    location_source = EXCLUDED.location_source,
                    updated_at = now()
                """,
                (
                    farm_id,
                    latitude,
                    longitude,
                    location_source,
                ),
            )

def list_sensor_readings(
    user_id: int,
    authorized_farm_codes: set[str],
    limit: int = 100,
    sensor_code: str | None = None,
    farm_code: str | None = None,
    zone_code: str | None = None,
) -> list[dict[str, Any]]:
    """Return newest sensor readings restricted to farms assigned to the user."""
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")

    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    sr.id,
                    f.farm_code,
                    z.zone_code,
                    s.sensor_code,
                    sr.recorded_at,
                    sr.temperature_c,
                    sr.humidity_pct,
                    sr.value,
                    sr.raw_payload
                FROM sensor_readings AS sr
                JOIN sensors AS s ON s.id = sr.sensor_id
                JOIN farms AS f ON f.id = s.farm_id
                JOIN zones AS z ON z.id = s.zone_id AND z.farm_id = s.farm_id
                WHERE f.farm_code = ANY(%s)
                  AND (%s IS NULL OR s.sensor_code = %s)
                  AND (%s IS NULL OR f.farm_code = %s)
                  AND (%s IS NULL OR z.zone_code = %s)
                ORDER BY sr.recorded_at DESC, sr.id DESC
                LIMIT %s
                """,
                (
                  sorted(authorized_farm_codes),
                  sensor_code,
                  sensor_code,
                  farm_code,
                  farm_code,
                  zone_code,
                  zone_code,
                  limit,
              ),
            )
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "farm_code": row[1],
            "zone_code": row[2],
            "sensor_code": row[3],
            "recorded_at": row[4],
            "temperature_c": row[5],
            "humidity_pct": row[6],
            "value": row[7],
            "raw_payload": row[8],
        }
        for row in rows
    ]



def list_farm_members(farm_code: str) -> list[dict[str, Any]]:
    """List members and their farm-scoped roles for one farm."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    u.email,
                    u.is_active,
                    r.name AS role_name
                FROM farms AS f
                JOIN farm_users AS fu ON fu.farm_id = f.id
                JOIN users AS u ON u.id = fu.user_id
                LEFT JOIN farm_user_roles AS fur
                    ON fur.farm_id = fu.farm_id
                   AND fur.user_id = fu.user_id
                LEFT JOIN roles AS r ON r.id = fur.role_id
                WHERE f.farm_code = %s
                ORDER BY u.username, u.id
                """,
                (farm_code,),
            )
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "is_active": row[3],
            "role": row[4],
        }
        for row in rows
    ]


def assign_farm_role(
    farm_code: str,
    user_id: int,
    role_name: str,
    assigned_by_user_id: int,
) -> bool:
    """Assign a role within one farm, enforcing the assigner's scope in SQL.

    Super Admin is a global role and cannot be assigned as a farm role.
    Farm Admin can assign only Operator or Viewer.
    Returns False if the farm, member, role, or authorization is invalid.
    """
    if role_name not in {"Farm Admin", "Operator", "Viewer"}:
        return False

    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                WITH assignment_context AS (
                    SELECT
                        f.id AS farm_id,
                        EXISTS (
                            SELECT 1
                            FROM farm_users AS target_membership
                            JOIN users AS target_user
                              ON target_user.id = target_membership.user_id
                            WHERE target_membership.farm_id = f.id
                              AND target_membership.user_id = %s
                              AND target_user.is_active = true
                        ) AS target_is_member,
                        EXISTS (
                            SELECT 1
                            FROM user_roles AS global_ur
                            JOIN roles AS global_role
                              ON global_role.id = global_ur.role_id
                            WHERE global_ur.user_id = %s
                              AND global_role.name = 'Super Admin'
                        ) AS actor_is_super_admin,
                        EXISTS (
                            SELECT 1
                            FROM farm_user_roles AS actor_fur
                            JOIN roles AS actor_role
                              ON actor_role.id = actor_fur.role_id
                            WHERE actor_fur.farm_id = f.id
                              AND actor_fur.user_id = %s
                              AND actor_role.name = 'Farm Admin'
                        ) AS actor_is_farm_admin,
                        (
                            SELECT r.id
                            FROM roles AS r
                            WHERE r.name = %s
                        ) AS role_id
                    FROM farms AS f
                    WHERE f.farm_code = %s
                )
                INSERT INTO farm_user_roles (
                    farm_id,
                    user_id,
                    role_id,
                    assigned_by_user_id,
                    assigned_at
                )
                SELECT
                    farm_id,
                    %s,
                    role_id,
                    %s,
                    now()
                FROM assignment_context
                WHERE target_is_member
                  AND role_id IS NOT NULL
                  AND (
                      actor_is_super_admin
                      OR (
                          actor_is_farm_admin
                          AND %s IN ('Operator', 'Viewer')
                      )
                  )
                ON CONFLICT (farm_id, user_id)
                DO UPDATE SET
                    role_id = EXCLUDED.role_id,
                    assigned_by_user_id = EXCLUDED.assigned_by_user_id,
                    assigned_at = EXCLUDED.assigned_at
                RETURNING farm_id
                """,
                (
                    user_id,
                    assigned_by_user_id,
                    assigned_by_user_id,
                    role_name,
                    farm_code,
                    user_id,
                    assigned_by_user_id,
                    role_name,
                ),
            )
            return cur.fetchone() is not None



def list_user_farm_codes_with_permission(
    user_id: int,
    permission: str,
) -> set[str]:
    """Return farm codes where a user has a specific permission."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT f.farm_code
                FROM farms AS f
                JOIN farm_users AS fu ON fu.farm_id = f.id
                JOIN farm_user_roles AS fur
                  ON fur.farm_id = fu.farm_id
                 AND fur.user_id = fu.user_id
                JOIN role_permissions AS rp ON rp.role_id = fur.role_id
                JOIN permissions AS p ON p.id = rp.permission_id
                WHERE fu.user_id = %s
                  AND p.name = %s

                UNION

                SELECT DISTINCT f.farm_code
                FROM farms AS f
                WHERE EXISTS (
                    SELECT 1
                    FROM user_roles AS ur
                    JOIN roles AS r ON r.id = ur.role_id
                    JOIN role_permissions AS rp ON rp.role_id = r.id
                    JOIN permissions AS p ON p.id = rp.permission_id
                    WHERE ur.user_id = %s
                      AND r.name = 'Super Admin'
                      AND p.name = %s
                )
                ORDER BY farm_code
                """,
                (user_id, permission, user_id, permission),
            )
            rows = cur.fetchall()

    return {row[0] for row in rows if row[0]}

def get_farm_user_permissions(
    user_id: int,
    farm_code: str,
) -> set[str]:
    """Return permissions granted by this farm's role plus global Super Admin."""
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT p.name
                FROM farms AS f
                JOIN farm_users AS fu ON fu.farm_id = f.id
                JOIN farm_user_roles AS fur
                  ON fur.farm_id = fu.farm_id
                 AND fur.user_id = fu.user_id
                JOIN role_permissions AS rp ON rp.role_id = fur.role_id
                JOIN permissions AS p ON p.id = rp.permission_id
                WHERE f.farm_code = %s
                  AND fu.user_id = %s

                UNION

                SELECT DISTINCT p.name
                FROM user_roles AS ur
                JOIN roles AS r ON r.id = ur.role_id
                JOIN role_permissions AS rp ON rp.role_id = r.id
                JOIN permissions AS p ON p.id = rp.permission_id
                WHERE ur.user_id = %s
                  AND r.name = 'Super Admin'
                """,
                (farm_code, user_id, user_id),
            )
            rows = cur.fetchall()

    return {row[0] for row in rows}
