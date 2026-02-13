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
    Temporary helper kept for reference and potential fallback:
    builds a simple CadQuery box from parameters.

    Newer phases execute user-provided CadQuery code instead; see
    `_execute_user_build`.
    """
    import cadquery as cq

    size = float(params.get("size", 10.0))
    # Numeric values are treated as millimetres end-to-end.
    wp = cq.Workplane("XY").box(size, size, size)
    return wp.val()


def _execute_user_build(code: str, params: Mapping[str, Any]) -> Any:
    """
    Execute user-provided CadQuery code and return the result of build(params).

    Contract:
    - User code must define a callable `build(params)` function.
    - `params` is the same mapping used for run_id computation.
    - `build` must return a CadQuery shape object (e.g. cq.Shape, Workplane.val())
      that `export_glb_from_shape` can handle.
    """
    import cadquery as cq

    # Provide a minimal, explicit global namespace for execution.
    exec_globals: dict[str, Any] = {
        "__builtins__": __builtins__,  # noqa: A001 - deliberate exposure for now
        "cq": cq,
        "cadquery": cq,
    }
    exec_locals: dict[str, Any] = {}

    try:
        compiled = compile(code, "<user_code>", "exec")
    except SyntaxError as exc:  # Let caller classify as "syntax" error.
        raise exc

    exec(compiled, exec_globals, exec_locals)

    # Merge namespaces to look up build() regardless of where it was defined.
    namespace: dict[str, Any] = {**exec_globals, **exec_locals}
    build = namespace.get("build")
    if not callable(build):
        raise RuntimeError("Expected a callable build(params) function in user code.")

    return build(params)


def execute_run(request: RunRequest) -> RunResponse:
    """
    Execute a CadQuery run request.

    Behaviour:
    - Computes deterministic run_id (code + stable(params)).
    - If artefact exists, returns it (cache hit).
    - Otherwise, executes user-provided CadQuery code and expects a
      `build(params)` function to return a shape that can be exported
      via OCCT to a single GLB artefact: 'model.glb'.
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
        shape = _execute_user_build(request.code, request.params)
        export_glb_from_shape(shape=shape, path=artifact_path)

        return RunResponse(
            run_id=run_id,
            status="ok",
            glb_url=f"/api/artifacts/{run_id}/model.glb",
        )
    except SyntaxError as exc:
        return RunResponse(
            run_id=run_id,
            status="error",
            error=ErrorInfo(
                type="syntax",
                message=str(exc),
                traceback=None,
            ),
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
