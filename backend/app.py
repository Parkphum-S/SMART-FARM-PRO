from typing import Literal
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

import dependencies
import mqtt_client
import persistence
import state_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client.connect()
    yield
    mqtt_client.disconnect()


app = FastAPI(
    title="Smart Farm Backend",
    lifespan=lifespan,
)


class LoginRequest(BaseModel):
    identifier: str
    password: str


@app.post("/api/v1/auth/login")
def login(body: LoginRequest):
    import auth
    import persistence

    user = persistence.get_user_for_auth(body.identifier)

    if user is None or not auth.verify_password(
        body.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    access_token = auth.create_access_token(str(user["id"]))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


class ActuatorCommand(BaseModel):
    command: Literal["on", "off"]
    request_id: str = Field(min_length=1, max_length=128)
    timestamp: datetime

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("request_id must not be blank")
        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value


@app.post(
    "/api/v1/farms/{farm_code}/zones/{zone_code}/actuators/{actuator_id}/command"
)
def send_actuator_command(
    farm_code: str,
    zone_code: str,
    actuator_id: str,
    body: ActuatorCommand,
    current_user: dict[str, object] = Depends(
        dependencies.require_farm_permission("actuator.control")
    ),
):
    topic = (
        f"farm/{farm_code}/zone/{zone_code}/"
        f"actuator/{actuator_id}/command"
    )
    timestamp = body.timestamp.isoformat()
    if timestamp.endswith("+00:00"):
        timestamp = timestamp[:-6] + "Z"

    payload = {
        "actuator_id": actuator_id,
        "command": body.command,
        "request_id": body.request_id,
        "timestamp": timestamp,
    }

    try:
        resolved_actuator_id = persistence.resolve_actuator_id(
            farm_code,
            zone_code,
            actuator_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Actuator authorization service unavailable",
        ) from exc

    if resolved_actuator_id is None:
        raise HTTPException(status_code=404, detail="Actuator not found")

    try:
        can_access = persistence.user_can_access_actuator(
            user_id=int(current_user["id"]),
            actuator_id=resolved_actuator_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Actuator authorization service unavailable",
        ) from exc

    if not can_access:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        persistence.insert_actuator_command(
            actuator_id=resolved_actuator_id,
            command=body.command,
            request_id=body.request_id,
            requested_at=timestamp,
            raw_payload=payload,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to record actuator command",
        ) from exc

    try:
        mqtt_client.publish(topic, payload)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to publish actuator command",
        ) from exc

    return {"status": "accepted", "request_id": body.request_id}

def _get_user_farm_state(
    current_user: dict[str, object],
    state: dict[str, dict[str, object]],
    permission: str,
) -> dict[str, dict[str, object]]:
    """Return only state from farms where the user has the required permission."""
    try:
        allowed_farms = persistence.list_user_farm_codes_with_permission(
            user_id=int(current_user["id"]),
            permission=permission,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Farm authorization service unavailable",
        ) from exc

    if not allowed_farms:
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
        )

    return {
        key: payload
        for key, payload in state.items()
        if isinstance(payload.get("farm_code"), str)
        and payload["farm_code"] in allowed_farms
    }

@app.get("/api/v1/esp32/status")
def get_esp32_status(
    current_user: dict[str, object] = Depends(
        dependencies.get_current_user
    ),
):
    return {
        "data": _get_user_farm_state(
            current_user,
            state_store.get_esp32_status(),
            "device.view",
        )
    }


@app.get("/api/v1/sensors/readings")
def get_sensor_readings(
    current_user: dict[str, object] = Depends(
        dependencies.get_current_user
    ),
):
    return {
        "data": _get_user_farm_state(
            current_user,
            state_store.get_sensor_readings(),
            "sensor.view",
        )
    }


@app.get("/api/v1/sensors/readings/history")
def get_sensor_reading_history(
    current_user: dict[str, object] = Depends(dependencies.get_current_user),
    limit: int = Query(default=100, ge=1, le=500),
    sensor_code: str | None = None,
    farm_code: str | None = None,
    zone_code: str | None = None,
):
    """Return persisted sensor history for farms the user may access."""
    try:
        authorized_farm_codes = persistence.list_user_farm_codes_with_permission(
            user_id=int(current_user["id"]), permission="sensor.history"
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Farm authorization service unavailable") from exc

    if not authorized_farm_codes or (farm_code is not None and farm_code not in authorized_farm_codes):
        raise HTTPException(status_code=403, detail="Forbidden")

    return {"data": persistence.list_sensor_readings(
        user_id=int(current_user["id"]), authorized_farm_codes=authorized_farm_codes,
        limit=limit, sensor_code=sensor_code, farm_code=farm_code, zone_code=zone_code,
    )}

@app.get("/api/v1/actuators/states")
def get_actuator_states(
    current_user: dict[str, object] = Depends(
        dependencies.get_current_user
    ),
):
    return {
        "data": _get_user_farm_state(
            current_user,
            state_store.get_actuator_states(),
            "actuator.view",
        )
    }
