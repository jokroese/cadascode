from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .models import ErrorInfo, RunRequest, RunResponse

ARTIFACTS_ROOT = Path(os.getenv("CADASCODE_ARTIFACTS_DIR", "artifacts")).resolve()


def _stable_params(params: Mapping[str, Any]) -> str:
    """Serialize params deterministically for hashing."""
    return json.dumps(params, sort_keys=True, separators=(",", ":"))


def _compute_run_id(code: str, params: Mapping[str, Any]) -> str:
    """Compute deterministic run_id = sha256(code + stable(params))."""
    h = hashlib.sha256()
    h.update(code.encode("utf-8"))
    h.update(b"\n--params--\n")
    h.update(_stable_params(params).encode("utf-8"))
    return h.hexdigest()


def _artifact_dir_for(run_id: str) -> Path:
    return ARTIFACTS_ROOT / run_id


def artifact_path_for(run_id: str) -> Path:
    return _artifact_dir_for(run_id) / "model.glb"


def _ensure_artifact_dir(run_id: str) -> Path:
    directory = _artifact_dir_for(run_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _write_placeholder_glb(path: Path) -> None:
    """TEMP: write a tiny placeholder GLB; to be replaced by real export."""
    # A real implementation will use OCC's RWGltf tooling or ocp-tessellate.
    # For now, write a small marker so clients can at least fetch a non-empty file.
    path.write_bytes(b"CADASC0DE_PLACEHOLDER_GLB")


def execute_run(request: RunRequest) -> RunResponse:
    """
    Execute a CadQuery run request.

    V0 implementation:
    - Computes deterministic run_id.
    - If artifact exists, short-circuits.
    - Otherwise, writes a placeholder GLB file.

    NOTE: This is intentionally minimal — the actual CadQuery execution and
    glTF/GLB export pipeline will be wired in later.
    """
    run_id = _compute_run_id(request.code, request.params)
    artifact_path = artifact_path_for(run_id)

    try:
        if artifact_path.is_file():
            return RunResponse(
                run_id=run_id,
                status="ok",
                glb_url=f"/api/artifacts/{run_id}/model.glb",
            )

        _ensure_artifact_dir(run_id)
        _write_placeholder_glb(artifact_path)

        return RunResponse(
            run_id=run_id,
            status="ok",
            glb_url=f"/api/artifacts/{run_id}/model.glb",
        )
    except Exception as exc:  # pragma: no cover - defensive catch-all
        return RunResponse(
            run_id=run_id,
            status="error",
            error=ErrorInfo(
                type="runtime",
                message=str(exc),
                traceback=None,
            ),
        )

