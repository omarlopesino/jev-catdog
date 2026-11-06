"""Configuration from the environment and the .env file: API key, base URL and Jev model."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from jev_catdog.jev.gateway import JevError

DEFAULT_BASE_URL = "https://api.typesafe.ai/v1"
DEFAULT_MODEL = "jev-latest"


@dataclass(frozen=True)
class Settings:
    """Values needed to call TypeSafe, already resolved and validated before use."""

    api_key: str
    base_url: str
    model: str

    @classmethod
    def from_env(cls, require_key: bool = True) -> "Settings":
        """Loads .env without overriding existing variables; requires JEV_API_KEY except in dry-run mode."""
        load_dotenv()
        api_key = os.environ.get("JEV_API_KEY", "").strip()
        if require_key and not api_key:
            raise JevError("missing_api_key", "Set JEV_API_KEY in the environment or in the .env file.")
        return cls(
            api_key=api_key,
            base_url=os.environ.get("JEV_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            model=os.environ.get("JEV_MODEL", DEFAULT_MODEL),
        )
