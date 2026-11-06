"""Turns results and errors into JSON: results go to stdout and errors to stderr."""

import json
import sys
from dataclasses import asdict

from jev_catdog.errors import AppError


def emit(result: object | None = None, request: dict | None = None) -> None:
    """Prints the result as JSON; when asked, adds the request sent under the request key."""
    output = asdict(result) if result is not None else {}
    if request is not None:
        output["request"] = request
    print(json.dumps(output, ensure_ascii=False, indent=2))


def fail(error: AppError) -> int:
    """Prints the normalized error on stderr and returns the process exit code."""
    output = {"error": error.code, "message": error.message, **error.details}
    print(json.dumps(output, ensure_ascii=False, indent=2), file=sys.stderr)
    return 1
