from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path


def test_health_import() -> None:
    """Ensure app.main can be imported as a package module."""
    root = Path(__file__).parent.parent
    sys.path.insert(0, str(root))

    module = import_module("app.main")
    assert hasattr(module, "app")
