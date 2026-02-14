from __future__ import annotations

import subprocess


class FormatError(RuntimeError):
    """Raised when code formatting fails."""


def format_code(code: str) -> str:
    """
    Format Python code using ruff.

    Pure function: no filesystem writes, no caching, no side effects.
    Uses ruff's stdin/stdout mode for in-memory formatting.

    Raises:
        FormatError: if ruff fails to format the code.
    """
    try:
        # ruff format --stdin-filename <name> reads from stdin and writes to stdout.
        # With text=True, input must be a *string*; let subprocess handle encoding.
        result = subprocess.run(
            ["ruff", "format", "--stdin-filename", "code.py"],
            input=code,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=5.0,  # prevent hanging on malformed input
        )
        return result.stdout
    except subprocess.CalledProcessError as exc:
        # ruff format returns non-zero on parse errors or other issues
        raise FormatError(f"Ruff formatting failed: {exc.stderr or str(exc)}") from exc
    except subprocess.TimeoutExpired as exc:
        raise FormatError("Formatting timed out") from exc
    except FileNotFoundError as exc:
        raise FormatError("ruff not found in PATH") from exc
