"""Request to Jev: state, questions and images, plus its exact JSON in readable form."""

from dataclasses import dataclass, field

from jev_catdog.jev.questions import Question


@dataclass(frozen=True)
class ImageAsset:
    """Image ready to send: JPEG bytes, source file name, and original and sent sizes."""

    data: bytes
    source: str
    original_size: tuple[int, int]
    sent_size: tuple[int, int]


@dataclass(frozen=True)
class JevRequest:
    """Everything asked to Jev in one call; images are referenced by name."""

    state: str | dict
    questions: dict[str, Question]
    images: dict[str, ImageAsset] = field(default_factory=dict)

    def payload(self, model: str) -> dict:
        """Builds the JSON that is sent; each image is declared in assets as a multipart part."""
        body = {
            "model": model,
            "state": self.state,
            "questions": {qid: q.to_payload() for qid, q in self.questions.items()},
        }
        if self.images:
            body["assets"] = {name: {"type": "image", "part": name} for name in self.images}
        return body

    def describe(self, model: str) -> dict:
        """Same as payload, but adds a readable summary of each image instead of its bytes."""
        body = self.payload(model)
        for name, image in self.images.items():
            body["assets"][name]["file"] = (
                f"{image.source} {_size(image.original_size)} -> {_size(image.sent_size)}"
            )
        return body


def _size(size: tuple[int, int]) -> str:
    """Formats a size as widthxheight for the image summaries shown to the user."""
    return f"{size[0]}x{size[1]}"
