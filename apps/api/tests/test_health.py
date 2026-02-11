from importlib import util as import_util
from pathlib import Path
from types import ModuleType


def test_health_import() -> None:
    """Smoke test: FastAPI app module can be imported from file path."""
    main_path = Path(__file__).parent.parent / "app" / "main.py"
    spec = import_util.spec_from_file_location("app.main", main_path)
    assert spec is not None
    module = import_util.module_from_spec(spec)
    assert isinstance(module, ModuleType)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert hasattr(module, "app")
