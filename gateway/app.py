from contextlib import asynccontextmanager

from fastapi import FastAPI

import mqtt_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client.connect()
    yield
    mqtt_client.disconnect()


app = FastAPI(
    title="Smart Farm Gateway",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}
