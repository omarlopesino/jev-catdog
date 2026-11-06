"""Typed Jev answers, built from the JSON that the API returns."""

from dataclasses import dataclass
from typing import Union

from jev_catdog.errors import AppError


class RefusalError(AppError):
    """Jev declined to answer a specific question; the affected question identifier is reported."""

    def __init__(self, question_id: str):
        super().__init__("refusal", f"Jev declined to answer question '{question_id}'.", question=question_id)


@dataclass(frozen=True)
class NoulAnswer:
    """Probability, between 0 and 1, that the statement of a noul question is true."""

    probability: float

    @classmethod
    def from_payload(cls, payload: dict) -> "NoulAnswer":
        """Reads the noul field of the API answer and stores it as a probability."""
        return cls(probability=payload["noul"])


@dataclass(frozen=True)
class ChoiceAnswer:
    """Option chosen by Jev, its confidence and the probability of every option offered."""

    choice: str
    confidence: float
    probabilities: dict[str, float]

    @classmethod
    def from_payload(cls, payload: dict) -> "ChoiceAnswer":
        """Reads the chosen option, the confidence and the probability split from the API."""
        return cls(payload["choice"], payload["confidence"], dict(payload["probabilities"]))


@dataclass(frozen=True)
class ScoreAnswer:
    """Expected score over the rubric, its confidence and the probability of each level."""

    score: float
    confidence: float
    probabilities: dict[int, float]

    @classmethod
    def from_payload(cls, payload: dict) -> "ScoreAnswer":
        """Reads the score and converts the level keys, which arrive as strings, into integers."""
        levels = {int(level): p for level, p in payload["probabilities"].items()}
        return cls(payload["score"], payload["confidence"], levels)


@dataclass(frozen=True)
class BoxAnswer:
    """Box around the target, with edges as fractions from the top-left corner."""

    top: float
    bottom: float
    left: float
    right: float
    confidence: float

    @classmethod
    def from_payload(cls, payload: dict) -> "BoxAnswer":
        """Reads the four edges of the box and the confidence of the box answer."""
        edges = payload["box"]
        return cls(edges["top"], edges["bottom"], edges["left"], edges["right"], payload["confidence"])

    def edges(self) -> dict[str, float]:
        """Returns the edges as a dictionary, ready to be shown in the JSON output."""
        return {"top": self.top, "bottom": self.bottom, "left": self.left, "right": self.right}


Answer = Union[NoulAnswer, ChoiceAnswer, ScoreAnswer, BoxAnswer]

_PARSERS = {
    "noul": NoulAnswer.from_payload,
    "choice": ChoiceAnswer.from_payload,
    "score": ScoreAnswer.from_payload,
    "box": BoxAnswer.from_payload,
}


def parse_answers(answers: dict) -> dict[str, Answer]:
    """Turns the API's answers block into typed answers keyed by question identifier."""
    parsed = {}
    for question_id, payload in answers.items():
        if payload["type"] == "refusal":
            raise RefusalError(question_id)
        parsed[question_id] = _PARSERS[payload["type"]](payload)
    return parsed
