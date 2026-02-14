from __future__ import annotations

from typing import Any, Literal, Mapping, Optional

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    """Request payload for executing CadQuery code."""

    code: str = Field(..., description="CadQuery Python code to execute.")
    params: Mapping[str, Any] = Field(
        default_factory=dict,
        description="Optional parameters made available to the execution context.",
    )


class ErrorInfo(BaseModel):
    """Structured error information returned on failure."""

    type: Literal["syntax", "runtime", "export"] = Field(
        ..., description="High-level error category."
    )
    message: str = Field(..., description="Human-readable error message.")
    traceback: Optional[str] = Field(
        default=None,
        description="Optional traceback text (for development).",
    )


class RunResponse(BaseModel):
    """Response payload for CadQuery execution."""

    run_id: str = Field(..., description="Deterministic hash of code + params.")
    status: Literal["ok", "error"] = Field(..., description="Execution status.")
    glb_url: Optional[str] = Field(
        default=None,
        description="URL to download the generated GLB model, if any.",
    )
    error: Optional[ErrorInfo] = Field(
        default=None,
        description="Error details when status == 'error'.",
    )


class FormatRequest(BaseModel):
    """Request payload for formatting Python code."""

    code: str = Field(..., description="Python code to format.")


class FormatResponse(BaseModel):
    """Response payload for code formatting."""

    formatted: str = Field(..., description="Formatted code string.")
