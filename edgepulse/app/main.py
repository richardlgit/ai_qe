from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from edgepulse.app.api.devices import router as devices_router
from edgepulse.app.database.config import Base, engine
from edgepulse.app.api.telemetry import router as telemetry_router
from edgepulse.app.database.telemetry_entity import TelemetryEntity 
from edgepulse.app.api.alerts import router as alerts_router
from edgepulse.app.database.alert_entity import AlertEntity  # noqa: F401


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="EdgePulse",
    description=(
        "Synthetic industrial IoT platform for "
        "AI-driven Quality Engineering"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(devices_router)
app.include_router(telemetry_router)
app.include_router(alerts_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "edgepulse",
    }