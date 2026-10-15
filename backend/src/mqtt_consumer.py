#!/usr/bin/env python3
"""Smart Farm Pro MQTT consumer for ESP32 sensor and relay telemetry."""

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt
import psycopg
from psycopg.types.json import Jsonb


FARM_CODE = "farm_001"
ZONE_CODE = "zone_01"
DEVICE_CODE = "esp32_001"
SENSOR_CODE = "am2305b_001"

MQTT_CONFIG = Path("/etc/smartfarm/mqtt.env")
DB_CONFIG = Path("/etc/smartfarm/postgres.env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("smart-farm-mqtt")

running = True
db = None


def stop_handler(_signum, _frame):
    global running
    running = False


def read_env(path):
    """Read KEY=VALUE config without printing secret values."""
    result = {}
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Invalid configuration line in {path.name}")
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def required(config, key):
    value = config.get(key, "")
    if not value:
        raise ValueError(f"Missing required configuration key: {key}")
    return value


def connect_db():
    config = read_env(DB_CONFIG)
    return psycopg.connect(
        host=required(config, "DB_HOST"),
        port=int(required(config, "DB_PORT")),
        dbname=required(config, "DB_DATABASE"),
        user=required(config, "DB_USERNAME"),
        password=required(config, "DB_PASSWORD"),
        connect_timeout=5,
        application_name="smart-farm-mqtt-consumer",
    )


def get_sensor_id(conn):
    row = conn.execute(
        """
        SELECT s.id
        FROM app.sensors s
        JOIN app.farms f ON f.id = s.farm_id
        JOIN app.zones z ON z.id = s.zone_id
        WHERE f.farm_code = %s
          AND z.zone_code = %s
          AND s.sensor_code = %s
          AND s.is_active = true
        """,
        (FARM_CODE, ZONE_CODE, SENSOR_CODE),
    ).fetchone()
    if row is None:
        raise RuntimeError("Configured active sensor was not found in PostgreSQL")
    return row[0]


def parse_timestamp(payload):
    raw = payload.get("timestamp")
    if not isinstance(raw, str) or not raw.strip():
        return datetime.now(timezone.utc)
    try:
        value = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def finite_number(payload, key, minimum=None, maximum=None):
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Invalid numeric field: {key}")
    value = float(value)
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError(f"Non-finite numeric field: {key}")
    if minimum is not None and value < minimum:
        raise ValueError(f"Field below permitted range: {key}")
    if maximum is not None and value > maximum:
        raise ValueError(f"Field above permitted range: {key}")
    return value


def save_sensor(payload):
    if payload.get("sensor_id") != SENSOR_CODE:
        raise ValueError("Sensor ID does not match configured sensor")
    temperature = finite_number(payload, "temperature_c", -50, 100)
    humidity = finite_number(payload, "humidity_pct", 0, 100)
    soil = finite_number(payload, "soil_moisture_pct", 0, 100)
    recorded_at = parse_timestamp(payload)

    with db.transaction():
        sensor_id = get_sensor_id(db)
        db.execute(
            """
            INSERT INTO app.sensor_readings
                (sensor_id, recorded_at, temperature_c, humidity_pct,
                 value, raw_payload)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (sensor_id, recorded_at, temperature, humidity, soil, Jsonb(payload)),
        )
    log.info(
        "Saved sensor reading sensor=%s temperature_c=%.2f humidity_pct=%.2f soil_moisture_pct=%.2f",
        SENSOR_CODE, temperature, humidity, soil,
    )


def save_device_status(payload):
    status = payload.get("status", payload.get("state", "online"))
    if not isinstance(status, str) or status.lower() not in {
        "online", "offline", "connected", "disconnected"
    }:
        raise ValueError("Invalid device status")
    status = status.lower()
    with db.transaction():
        result = db.execute(
            """
            UPDATE app.devices d
            SET status = %s, last_seen_at = now(), updated_at = now()
            FROM app.farms f
            WHERE d.farm_id = f.id
              AND f.farm_code = %s
              AND d.device_code = %s
            """,
            (status, FARM_CODE, DEVICE_CODE),
        )
        if result.rowcount != 1:
            raise RuntimeError("Configured device was not found in PostgreSQL")
    log.info("Updated device status device=%s status=%s", DEVICE_CODE, status)


def handle_relay(topic, payload):
    parts = topic.split("/")
    # farm/<farm>/zone/<zone>/actuator/<actuator_id>/state
    if len(parts) != 7 or parts[0] != "farm" or parts[2] != "zone":
        raise ValueError("Unexpected actuator topic")
    if parts[1] != FARM_CODE or parts[3] != ZONE_CODE or parts[4] != "actuator":
        raise ValueError("Actuator topic does not match configured farm and zone")
    if parts[6] != "state":
        raise ValueError("Only actuator state messages are accepted")

    topic_actuator_id = parts[5]
    legacy_mapping = {
        "irrigation_pump_001": "relay_01",
        "water_pump_01": "relay_03",
        "oxygen_pump_01": "relay_04",
    }
    relay_codes = {"relay_01", "relay_02", "relay_03", "relay_04"}

    if topic_actuator_id in legacy_mapping:
        if payload.get("actuator_id") != topic_actuator_id:
            raise ValueError("Actuator ID does not match topic")
        relay_code = legacy_mapping[topic_actuator_id]
    elif topic_actuator_id in relay_codes:
        if payload.get("actuator_id") != topic_actuator_id:
            raise ValueError("Actuator ID does not match topic")
        relay_code = topic_actuator_id
    else:
        raise ValueError(f"Unknown actuator ID: {topic_actuator_id}")

    state = payload.get("actual_state", payload.get("state"))
    if not isinstance(state, str) or state.lower() not in {"on", "off", "unknown"}:
        raise ValueError("Invalid relay state")
    state = state.lower()
    recorded_at = parse_timestamp(payload)

    with db.transaction():
        row = db.execute(
            """
            UPDATE app.actuators a
            SET state = %s, updated_at = now()
            FROM app.farms f, app.zones z
            WHERE a.farm_id = f.id
              AND a.zone_id = z.id
              AND f.farm_code = %s
              AND z.zone_code = %s
              AND a.actuator_code = %s
              AND a.device_id = (
                  SELECT d.id FROM app.devices d
                  WHERE d.farm_id = f.id AND d.device_code = %s
              )
            RETURNING a.id
            """,
            (state, FARM_CODE, ZONE_CODE, relay_code, DEVICE_CODE),
        ).fetchone()
        if row is None:
            raise RuntimeError(f"Configured relay was not found: {relay_code}")
        db.execute(
            """
            INSERT INTO app.actuator_states
                (actuator_id, state, recorded_at, raw_payload)
            VALUES (%s, %s, %s, %s)
            """,
            (row[0], state, recorded_at, Jsonb(payload)),
        )
    log.info("Saved relay state actuator=%s state=%s", relay_code, state)


def main():
    global db
    mqtt_config = read_env(MQTT_CONFIG)
    db = connect_db()
    try:
        get_sensor_id(db)
    finally:
        db.close()
        db = None

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="smart-farm-pro-consumer",
        protocol=mqtt.MQTTv311,
    )
    client.username_pw_set(
        required(mqtt_config, "MQTT_BACKEND_USERNAME"),
        required(mqtt_config, "MQTT_BACKEND_PASSWORD"),
    )

    def on_connect(client, _userdata, _flags, reason_code, _properties):
        if reason_code.is_failure:
            log.error("MQTT connection failed: %s", reason_code)
            return
        log.info("Connected to MQTT broker")
        client.subscribe([
            (f"farm/{FARM_CODE}/zone/{ZONE_CODE}/sensor/{SENSOR_CODE}/reading", 1),
            (f"farm/{FARM_CODE}/esp32/{DEVICE_CODE}/status", 1),
            (f"farm/{FARM_CODE}/zone/{ZONE_CODE}/actuator/+/state", 1),
        ])

    def on_message(_client, _userdata, message):
        global db
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("MQTT payload must be a JSON object")
            if db is None or db.closed:
                db = connect_db()

            if message.topic.endswith(f"/sensor/{SENSOR_CODE}/reading"):
                save_sensor(payload)
            elif message.topic == f"farm/{FARM_CODE}/esp32/{DEVICE_CODE}/status":
                save_device_status(payload)
            elif "/actuator/" in message.topic and message.topic.endswith("/state"):
                if message.retain:
                    log.info("Ignoring retained actuator state topic=%s", message.topic)
                else:
                    handle_relay(message.topic, payload)
            else:
                log.warning("Ignoring unsupported MQTT topic")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            log.warning("Rejected invalid MQTT message: %s", exc)
        except Exception:
            log.exception("Failed to process MQTT message")
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass
                db = None

    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)

    try:
        client.connect_async(
            required(mqtt_config, "MQTT_HOST"),
            int(required(mqtt_config, "MQTT_PORT")),
            keepalive=60,
        )
        client.loop_start()

        while running:
            time.sleep(1)
    finally:
        client.disconnect()
        client.loop_stop()
        if db is not None:
            db.close()
            db = None


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("MQTT consumer startup failed")
        sys.exit(1)
