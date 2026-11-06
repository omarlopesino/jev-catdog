"""Example 5, box with an image: locates the cat's or dog's face and saves the crop."""

from dataclasses import dataclass
from pathlib import Path

from jev_catdog.errors import AppError
from jev_catdog.jev.gateway import JevGateway
from jev_catdog.jev.questions import Box, Noul
from jev_catdog.jev.request import JevRequest
from jev_catdog.use_cases.ports import Cropper, ImageLoader, load_image

# Box always returns a box; the companion noul tells whether there really is a face.
QUESTIONS = {
    "has_face": Noul(instructions="Is the face of a cat or a dog visible in `photo`?"),
    "face": Box(instructions="The face of the cat or dog in `photo`."),
}

DEFAULT_THRESHOLD = 0.5


@dataclass(frozen=True)
class CropFaceResult:
    """Box of the face found, the probability that it exists, confidence and the crop's path."""

    image: str
    face_found: bool
    face_probability: float
    confidence: float
    box: dict[str, float]
    output: str


class CropAnimalFace:
    """Asks Jev for the animal's face and crops the original photo if it passes the threshold."""

    def __init__(self, gateway: JevGateway, loader: ImageLoader, cropper: Cropper):
        self._gateway = gateway
        self._loader = loader
        self._cropper = cropper

    def request_for(self, path: Path) -> JevRequest:
        """A single request carrying the companion noul and the box over the same photo."""
        return JevRequest(
            state={"photo": "photo"},
            questions=QUESTIONS,
            images={"photo": load_image(self._loader, path)},
        )

    def execute(self, path: Path, destination: Path, threshold: float = DEFAULT_THRESHOLD) -> CropFaceResult:
        """Crops and saves the face; if the noul falls below the threshold, raises face_not_found."""
        answers = self._gateway.decide(self.request_for(path))
        face_probability = answers["has_face"].probability
        if face_probability < threshold:
            raise AppError(
                "face_not_found",
                "No cat or dog face was found in the image.",
                image=str(path),
                face_probability=face_probability,
            )
        box = answers["face"]
        output = self._cropper.crop(path, box, destination)
        return CropFaceResult(str(path), True, face_probability, box.confidence, box.edges(), str(output))
