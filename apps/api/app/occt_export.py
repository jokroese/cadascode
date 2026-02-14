from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, cast


class ExportError(RuntimeError):
    """Raised when GLB export fails."""


class _HasWrapped(Protocol):
    # CadQuery shape objects generally expose .wrapped (TopoDS_Shape)
    wrapped: Any


def _as_topods_shape(shape: Any) -> Any:
    """
    Best-effort extraction of TopoDS_Shape from CadQuery objects.
    - cq.Shape: has `.wrapped`
    - cq.Workplane.val(): returns cq.Shape
    """
    if hasattr(shape, "wrapped"):
        return cast(_HasWrapped, shape).wrapped
    raise ExportError(
        "Unsupported shape type: expected a CadQuery shape with `.wrapped` (TopoDS_Shape)."
    )


def export_glb_from_shape(shape: Any, path: Path) -> None:
    """
    Export a CadQuery/OCP shape to binary glTF (.glb) using OCCT's XDE + RWGltf_CafWriter pipeline.

    Determinism considerations:
    - Meshing is run single-threaded (no parallelism).
    - Fixed linear/angular deflection values.
    - No timestamps or random IDs are injected.

    Raises:
        ExportError: on any export/OCCT failure.
    """
    try:
        # Runtime imports so the rest of the app can import without pulling in
        # heavy OCCT bindings up front. Types are provided via local OCP stubs
        # under apps/api/typings for pyright.
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.Message import Message_ProgressRange
        from OCP.RWGltf import RWGltf_CafWriter
        from OCP.TCollection import TCollection_AsciiString, TCollection_ExtendedString
        from OCP.TColStd import TColStd_IndexedDataMapOfStringString
        from OCP.TDocStd import TDocStd_Document
        from OCP.XCAFDoc import XCAFDoc_DocumentTool
    except Exception as exc:  # pragma: no cover
        raise ExportError(f"Failed to import OCP export modules: {exc}") from exc

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    topods_shape = _as_topods_shape(shape)

    # 1) Create an XDE (XCAF) document to host the shape.
    # XCAF documents are the expected input for RWGltf_CafWriter.
    label = TCollection_ExtendedString("MDTV-XCAF")
    doc = TDocStd_Document(label)
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    shape_tool.AddShape(topods_shape, False)

    # 2) Ensure triangulation exists (writer requires it).
    # Use deterministic, single-threaded meshing; treat units as millimetres.
    linear_deflection = 0.1
    angular_deflection = 0.5
    is_relative = False
    in_parallel = False
    BRepMesh_IncrementalMesh(
        topods_shape,
        linear_deflection,
        is_relative,
        angular_deflection,
        in_parallel,
    )

    # 3) Write GLB via RWGltf_CafWriter in binary mode (.glb).
    writer = RWGltf_CafWriter(TCollection_AsciiString(str(out)), True)

    # Optional but usually desirable for web: fewer primitives / smaller JSON sections.
    writer.SetMergeFaces(True)
    writer.SetSplitIndices16(True)

    file_info = TColStd_IndexedDataMapOfStringString()
    progress = Message_ProgressRange()
    ok = writer.Perform(doc, file_info, progress)
    if not ok or not out.is_file() or out.stat().st_size == 0:
        raise ExportError("RWGltf_CafWriter failed to write a valid .glb file.")
