"""Example 4, score with an image: a cat-to-dog scale, a counterexample to choice."""

from dataclasses import dataclass
from pathlib import Path

from jev_catdog.jev.gateway import JevGateway
from jev_catdog.jev.questions import Score
from jev_catdog.jev.request import JevRequest
from jev_catdog.use_cases.ports import ImageLoader, load_image

QUESTIONS = {
    "cat_to_dog": Score(
        instructions="Where does the animal in `photo` fall between a cat and a dog?",
        criteria=["The animal is clearly a cat", "The animal is clearly a dog"],
    ),
}

NOTE = "Score assumes ordered levels; for unordered categories such as cat or dog, choice is a better fit."


@dataclass(frozen=True)
class ScoreCatDogResult:
    """Score from 0 (cat) to 1 (dog), its confidence and the probability of each end."""

    image: str
    score: float
    confidence: float
    cat_probability: float
    dog_probability: float
    note: str


class ScoreCatDog:
    """Rates a photo with score on the cat-dog scale and splits the probability between both."""

    def __init__(self, gateway: JevGateway, loader: ImageLoader):
        self._gateway = gateway
        self._loader = loader

    def request_for(self, path: Path) -> JevRequest:
        """Attaches the photo as photo and applies the two-level rubric, from cat to dog."""
        return JevRequest(
            state={"photo": "photo"},
            questions=QUESTIONS,
            images={"photo": load_image(self._loader, path)},
        )

    def execute(self, path: Path) -> ScoreCatDogResult:
        """Level 0 is cat and level 1 is dog; their probabilities are returned separately."""
        answer = self._gateway.decide(self.request_for(path))["cat_to_dog"]
        return ScoreCatDogResult(
            str(path), answer.score, answer.confidence, answer.probabilities[0], answer.probabilities[1], NOTE
        )
