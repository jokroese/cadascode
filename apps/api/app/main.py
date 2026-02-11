from fastapi import FastAPI

app = FastAPI(title="Cadascode API", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    """Simple health endpoint for smoke tests."""
    return {"status": "ok"}
