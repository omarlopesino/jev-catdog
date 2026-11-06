"""Example 3, choice with an image: decides whether the photo shows a cat, a dog or something else."""

from dataclasses import dataclass
from pathlib import Path

from jev_catdog.jev.gateway import JevGateway
from jev_catdog.jev.questions import Choice
from jev_catdog.jev.request import JevRequest
from jev_catdog.use_cases.ports import ImageLoader, load_image

QUESTIONS = {
    "animal": Choice(
        instructions="What does `photo` mainly show?",
        criteria={
            "cat": "A cat",
            "dog": "A dog",
            "other": "Anything that is neither a cat nor a dog",
        },
    ),
}


@dataclass(frozen=True)
class ChooseCatDogResult:
    """Chosen option (cat, dog or other), its confidence and the probability of each option."""

    image: str
    choice: str
    confidence: float
    probabilities: dict[str, float]


class ChooseCatDog:
    """Classifies a photo with choice as cat, dog or something else, assuming no order at all."""

    def __init__(self, gateway: JevGateway, loader: ImageLoader):
        self._gateway = gateway
        self._loader = loader

    def request_for(self, path: Path) -> JevRequest:
        """Attaches the photo as photo and offers the three options with a short description."""
        return JevRequest(
            state={"photo": "photo"},
            questions=QUESTIONS,
            images={"photo": load_image(self._loader, path)},
        )

    def execute(self, path: Path) -> ChooseCatDogResult:
        """Sends the photo and returns the chosen option along with the full probability split."""
        answer = self._gateway.decide(self.request_for(path))["animal"]
        return ChooseCatDogResult(str(path), answer.choice, answer.confidence, answer.probabilities)
