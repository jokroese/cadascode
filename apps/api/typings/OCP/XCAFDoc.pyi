from typing import Any

class XCAFDoc_ShapeTool:
    def AddShape(self, shape: Any, make_assembly: bool = False) -> Any: ...

class XCAFDoc_DocumentTool:
    @staticmethod
    def ShapeTool_s(main_label: Any) -> XCAFDoc_ShapeTool: ...
