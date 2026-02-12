from __future__ import annotations

import sys
from pathlib import Path


def test_execute_run_creates_artifact_and_is_deterministic(tmp_path: Path) -> None:
    """Smoke test for executor without relying on package layout."""
    root = Path(__file__).parent.parent
    sys.path.insert(0, str(root))

    from app import executor  # type: ignore[import]
    from app.models import RunRequest  # type: ignore[import]

    original_root = executor.ARTIFACTS_ROOT
    try:
        executor.ARTIFACTS_ROOT = tmp_path / "artifacts"

        request = RunRequest(code="result = 1", params={"a": 1})
        response1 = executor.execute_run(request)
        response2 = executor.execute_run(request)

        assert response1.status == "ok"
        assert response2.status == "ok"
        assert response1.run_id == response2.run_id

        artifact = executor.artifact_path_for(response1.run_id)
        assert artifact.is_file()
        assert artifact.read_bytes()  # non-empty placeholder
    finally:
        executor.ARTIFACTS_ROOT = original_root

