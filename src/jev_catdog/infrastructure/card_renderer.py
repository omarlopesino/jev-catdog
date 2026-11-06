"""Draws the summary card of each command's result, the image counterpart of the JSON output."""

from pathlib import Path

from jev_catdog.errors import AppError
from jev_catdog.infrastructure.card_canvas import (
    CONTENT_WIDTH,
    MUTED,
    PADDING,
    ROW_HEIGHT,
    ROW_TOP,
    Card,
    display,
    sans,
)
from jev_catdog.use_cases.choose_cat_dog import ChooseCatDogResult
from jev_catdog.use_cases.crop_animal_face import CropFaceResult
from jev_catdog.use_cases.detect_cat_in_image import CatInImageResult
from jev_catdog.use_cases.detect_cat_in_text import CatInTextResult
from jev_catdog.use_cases.score_cat_dog import ScoreCatDogResult

GAP = 48
TILE = ROW_HEIGHT
CROP_IMAGE_HEIGHT = 350

GREEN, ORANGE, RED = "#1E7A3E", "#B35A00", "#C0262D"
# Fixed per class, apart from the probability traffic light, so a dog is always the same colour.
CLASS_COLORS = {"cat": "#2D55C8", "dog": ORANGE, "other": "#4A4F5A"}


class CardRenderer:
    """Turns a use case result, or the face_not_found error, into a PNG card at the given path."""

    def render(self, result: object, destination: Path) -> Path:
        """Picks the layout from the result type and saves the card to destination."""
        match result:
            case CatInTextResult():
                card = self._noul("cat-detect-text · noul", "Is this a cat?", result.is_cat_probability)
                card.quote(result.input, (PADDING, ROW_TOP, _beside_tile(), ROW_HEIGHT))
            case CatInImageResult():
                card = self._noul("cat-detect-image · noul", "Is there a cat in the photo?", result.is_cat_probability)
                card.photo(Path(result.image), (PADDING, ROW_TOP, _beside_tile(), ROW_HEIGHT))
            case ChooseCatDogResult():
                card = Card("choice-cat-dog · choice", "Cat, dog or other?")
                card.photo(Path(result.image), (PADDING, ROW_TOP, _beside_tile(), ROW_HEIGHT))
                card.tile(
                    _tile_box(),
                    CLASS_COLORS.get(result.choice, CLASS_COLORS["other"]),
                    [("classified as", sans(26)), (result.choice.capitalize(), display(120))],
                )
            case ScoreCatDogResult():
                card = self._score(result)
            case CropFaceResult():
                card = self._crop(Path(result.image), f"Face · {_percent(result.face_probability)} confidence")
                card.photo(Path(result.output), (PADDING, ROW_TOP, TILE, CROP_IMAGE_HEIGHT))
            case _:
                raise TypeError(f"No card layout for {type(result).__name__}.")
        return card.save(destination)

    def render_failure(self, error: AppError, destination: Path) -> Path | None:
        """Draws the not-found card for face_not_found; other errors have no card and return None."""
        if error.code != "face_not_found":
            return None
        probability = error.details["face_probability"]
        card = self._crop(Path(error.details["image"]), f"No face found · {_percent(probability)} confidence")
        card.missing((PADDING, ROW_TOP, TILE, CROP_IMAGE_HEIGHT))
        return card.save(destination)

    def _noul(self, tag: str, title: str, probability: float) -> Card:
        """Card with the traffic-light tile on the right; the caller fills the left panel."""
        card = Card(tag, title)
        card.tile(
            _tile_box(),
            _traffic_light(probability),
            [(_percent(probability), display(156)), ("chance it is a cat", sans(26))],
        )
        return card

    def _score(self, result: ScoreCatDogResult) -> Card:
        """Photo on the left and two tiles side by side for the cat and dog probabilities."""
        width, gap = 560, 20
        card = Card("score-cat-dog · score", "Cat or dog?")
        card.photo(Path(result.image), (PADDING, ROW_TOP, CONTENT_WIDTH - GAP - width, ROW_HEIGHT))
        left = PADDING + CONTENT_WIDTH - width
        half = (width - gap) // 2
        for index, (label, probability) in enumerate([("Cat", result.cat_probability), ("Dog", result.dog_probability)]):
            card.tile(
                (left + index * (half + gap), ROW_TOP, half, ROW_HEIGHT),
                CLASS_COLORS[label.lower()],
                [(_percent(probability), display(108)), (label, sans(28))],
            )
        return card

    def _crop(self, original: Path, caption: str) -> Card:
        """Crop card with the original on the right; the caller fills the left panel above caption."""
        card = Card("crop-cat-dog-face · box", "Find the face")
        right = PADDING + TILE + GAP
        card.photo(original, (right, ROW_TOP, CONTENT_WIDTH - TILE - GAP, CROP_IMAGE_HEIGHT))
        caption_top = ROW_TOP + CROP_IMAGE_HEIGHT + 14
        card.caption(caption, PADDING, caption_top)
        card.caption("Original", right, caption_top, MUTED)
        return card


def _tile_box() -> tuple[int, int, int, int]:
    """The square result tile on the right of the row, as tall as the row so its edges meet the photo's."""
    return PADDING + CONTENT_WIDTH - TILE, ROW_TOP, TILE, TILE


def _beside_tile() -> int:
    """Width left for the photo or quote next to the square tile."""
    return CONTENT_WIDTH - TILE - GAP


def _traffic_light(probability: float) -> str:
    """Green from 75%, orange from 40%, red below."""
    if probability >= 0.75:
        return GREEN
    return ORANGE if probability >= 0.4 else RED


def _percent(probability: float) -> str:
    """A probability as a whole percentage, e.g. 0.97 as 97%."""
    return f"{round(probability * 100)}%"
