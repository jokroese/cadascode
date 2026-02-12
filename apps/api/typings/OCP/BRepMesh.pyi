from typing import Any

class BRepMesh_IncrementalMesh:
    def __init__(
        self,
        shape: Any,
        linear_deflection: float,
        is_relative: bool,
        angular_deflection: float,
        in_parallel: bool,
    ) -> None: ...
