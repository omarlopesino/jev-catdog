"""Jev question types; each one knows how to serialize itself to the API's JSON format."""

from dataclasses import dataclass
from typing import Protocol


class Question(Protocol):
    """Common contract: any question turns into the dictionary the API expects."""

    def to_payload(self) -> dict:
        """Returns the question's dictionary exactly as it appears inside questions in the API."""
        ...


@dataclass(frozen=True)
class Noul:
    """Yes/no question; Jev returns the probability that the statement is true."""

    instructions: str

    def to_payload(self) -> dict:
        """Serializes the noul question with its instructions so it can be sent to Jev."""
        return {"type": "noul", "instructions": self.instructions}


@dataclass(frozen=True)
class Choice:
    """Picks one option among several; Jev returns the chosen one and each option's probability."""

    instructions: str
    criteria: dict[str, str | None]

    def to_payload(self) -> dict:
        """Serializes the choice question with its options and a description for each one."""
        return {"type": "choice", "instructions": self.instructions, "criteria": dict(self.criteria)}


@dataclass(frozen=True)
class Score:
    """Rates against a rubric ordered from low to high; Jev returns the expected value."""

    instructions: str
    criteria: list[str]

    def to_payload(self) -> dict:
        """Serializes the score question with its levels ordered from lowest to highest."""
        return {"type": "score", "instructions": self.instructions, "criteria": list(self.criteria)}


@dataclass(frozen=True)
class Box:
    """Locates a target in an image; Jev returns its edges as fractions of the size."""

    instructions: str

    def to_payload(self) -> dict:
        """Serializes the box question; it only carries instructions because criteria are not allowed."""
        return {"type": "box", "instructions": self.instructions}
