from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .models import ErrorInfo, RunRequest, RunResponse
from .occt_export import ExportError, export_glb_from_shape

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


def _build_shape_from_params(params: Mapping[str, Any]) -> Any:
    """
    Temporary hard-coded CadQuery model for v0 CadQuery → viewer wiring.

    This will be replaced in a later step by executing user-provided CadQuery
    code (via a build(params) function) once Monaco is wired in.
    """
    import cadquery as cq

    size = float(params.get("size", 10.0))
    # Numeric values are treated as millimetres end-to-end.
    wp = cq.Workplane("XY").box(size, size, size)
    return wp.val()


def execute_run(request: RunRequest) -> RunResponse:
    """
    Execute a CadQuery run request.

    Phase 3a implementation:
    - Computes deterministic run_id.
    - If artifact exists, short-circuits.
    - Otherwise, builds a hard-coded CadQuery model and exports it to GLB
      using OCCT's RWGltf_CafWriter, producing exactly one artefact:
      'model.glb'.
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
        shape = _build_shape_from_params(request.params)
        export_glb_from_shape(shape=shape, path=artifact_path)

        return RunResponse(
            run_id=run_id,
            status="ok",
            glb_url=f"/api/artifacts/{run_id}/model.glb",
        )
    except ExportError as exc:
        return RunResponse(
            run_id=run_id,
            status="error",
            error=ErrorInfo(
                type="export",
                message=str(exc),
                traceback=None,
            ),
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
