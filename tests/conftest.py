"""Shared test doubles: a fake gateway that records requests and a loader that skips the disk."""

from pathlib import Path

import pytest

from jev_catdog.jev.answers import parse_answers
from jev_catdog.jev.request import ImageAsset, JevRequest


class FakeGateway:
    """Network-free gateway that keeps the last request and replies with the configured JSON."""

    model = "jev-test"

    def __init__(self, answers: dict):
        self._answers = answers
        self.last_request: JevRequest | None = None

    def decide(self, request: JevRequest):
        """Records the received request and returns the configured answers, already typed."""
        self.last_request = request
        return parse_answers(self._answers)


class FakeLoader:
    """Loader that never reads the image; it returns fixed bytes with the file name."""

    def prepare(self, path: Path) -> ImageAsset:
        """Returns a fake 1280x853 asset so the use case tests do not depend on Pillow."""
        return ImageAsset(b"jpeg", path.name, (1280, 853), (1280, 853))


@pytest.fixture
def cat_image() -> Path:
    """Path to a real dataset image, used when the use case checks that the file exists."""
    return Path(__file__).parent.parent / "data" / "cats" / "cats_01.jpg"
