from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .executor import artifact_path_for, execute_run
from .formatter import FormatError, format_code
from .models import FormatRequest, FormatResponse, RunRequest, RunResponse

app = FastAPI(title="Cadascode API", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    """Simple health endpoint for smoke tests."""
    return {"status": "ok"}


@app.post("/api/run", response_model=RunResponse)
def run_cadquery(request: RunRequest) -> RunResponse:
    """
    Execute CadQuery code and return a run descriptor.

    For now this writes a placeholder GLB artifact and returns its URL.
    """
    return execute_run(request)


@app.get("/api/artifacts/{run_id}/model.glb")
def get_artifact_glb(run_id: str) -> FileResponse:
    """Return the GLB artifact for a given run id."""
    path: Path = artifact_path_for(run_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Artifact not found")

    return FileResponse(path, media_type="model/gltf-binary", filename="model.glb")


@app.post("/api/format", response_model=FormatResponse)
def format_python_code(request: FormatRequest) -> FormatResponse:
    """
    Format Python code using ruff.

    Pure endpoint: no filesystem writes, no caching, no side effects.
    Returns formatted code string.
    """
    try:
        formatted = format_code(request.code)
        return FormatResponse(formatted=formatted)
    except FormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
