"""Example 2, noul with an image: probability that a cat appears in a photo."""

from dataclasses import dataclass
from pathlib import Path

from jev_catdog.jev.gateway import JevGateway
from jev_catdog.jev.questions import Noul
from jev_catdog.jev.request import JevRequest
from jev_catdog.use_cases.ports import ImageLoader, load_image

QUESTIONS = {
    "is_cat": Noul(instructions="Is there a cat in `photo`?"),
}


@dataclass(frozen=True)
class CatInImageResult:
    """Path of the analysed image and the probability, between 0 and 1, that it contains a cat."""

    image: str
    is_cat_probability: float


class DetectCatInImage:
    """Asks Jev with noul whether the given photo contains at least one cat."""

    def __init__(self, gateway: JevGateway, loader: ImageLoader):
        self._gateway = gateway
        self._loader = loader

    def request_for(self, path: Path) -> JevRequest:
        """The photo is attached as photo and the state references it by that same name."""
        return JevRequest(
            state={"photo": "photo"},
            questions=QUESTIONS,
            images={"photo": load_image(self._loader, path)},
        )

    def execute(self, path: Path) -> CatInImageResult:
        """Sends the photo and returns the probability that there is a cat in it."""
        answers = self._gateway.decide(self.request_for(path))
        return CatInImageResult(str(path), answers["is_cat"].probability)
