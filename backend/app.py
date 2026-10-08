from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import mqtt_client
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
    command: str
    request_id: str
    timestamp: str


@app.post("/api/v1/actuators/{actuator_id}/command")
def send_actuator_command(actuator_id: str, body: ActuatorCommand):
    topic = f"farm/farm_001/zone/zone_01/actuator/{actuator_id}/command"
    payload = {
        "actuator_id": actuator_id,
        "command": body.command,
        "request_id": body.request_id,
        "timestamp": body.timestamp,
    }
    mqtt_client.publish(topic, payload)
    return {"status": "accepted", "request_id": body.request_id}


@app.get("/api/v1/esp32/status")
def get_esp32_status():
    return {"data": state_store.get_esp32_status()}


@app.get("/api/v1/sensors/readings")
def get_sensor_readings():
    return {"data": state_store.get_sensor_readings()}


@app.get("/api/v1/actuators/states")
def get_actuator_states():
    return {"data": state_store.get_actuator_states()}
