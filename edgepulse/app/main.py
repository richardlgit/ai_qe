from fastapi import FastAPI

app = FastAPI(
    title="EdgePulse",
    description="Synthetic industrial IoT platform for AI-driven Quality Engineering",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "edgepulse",
    }