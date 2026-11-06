"""Port to Jev: use cases depend on this abstraction, not on the HTTP client."""

from typing import Protocol

from jev_catdog.errors import AppError
from jev_catdog.jev.answers import Answer
from jev_catdog.jev.request import JevRequest


class JevError(AppError):
    """Failure while talking to Jev: missing credentials, an HTTP error or an unexpected response."""


class JevGateway(Protocol):
    """Sends a request to Jev and returns the typed answers keyed by question identifier."""

    model: str

    def decide(self, request: JevRequest) -> dict[str, Answer]:
        """Sends the request and returns each typed answer under its question's identifier."""
        ...
