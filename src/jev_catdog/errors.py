"""Application error with a normalized code, a message and details for the JSON output."""


class AppError(Exception):
    """Expected failure that the CLI prints as JSON on stderr with exit code 1."""

    def __init__(self, code: str, message: str, **details):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
