"""Tests of the PNG summary cards: size, the tile colour each result picks, and the not-found card."""

from pathlib import Path

import pytest
from PIL import Image

from jev_catdog.errors import AppError
from jev_catdog.infrastructure.card_canvas import HEIGHT, ROW_TOP, SCALE, WIDTH
from jev_catdog.infrastructure.card_renderer import CardRenderer
from jev_catdog.use_cases.choose_cat_dog import ChooseCatDogResult
from jev_catdog.use_cases.crop_animal_face import CropFaceResult
from jev_catdog.use_cases.detect_cat_in_image import CatInImageResult
from jev_catdog.use_cases.detect_cat_in_text import CatInTextResult
from jev_catdog.use_cases.score_cat_dog import ScoreCatDogResult

DATA = Path(__file__).parent.parent / "data"
CAT = DATA / "cats" / "cats_01.jpg"
# A point inside the right-hand tile, clear of its rounded corner and its text.
TILE_POINT = ((1144 - 20) * SCALE, (ROW_TOP + 40) * SCALE)


def _pixel(path: Path, point: tuple[int, int]) -> str:
    """Colour of one pixel of the saved card, as an upper-case hex string."""
    with Image.open(path) as card:
        return "#{:02X}{:02X}{:02X}".format(*card.convert("RGB").getpixel(point))


@pytest.mark.parametrize(
    ("probability", "color"), [(0.89, "#1E7A3E"), (0.5, "#B35A00"), (0.2, "#C0262D")]
)
def test_text_card_tile_follows_traffic_light(tmp_path, probability, color):
    card = CardRenderer().render(CatInTextResult("It meows and eats tuna", probability), tmp_path / "c.png")
    with Image.open(card) as image:
        assert image.size == (WIDTH * SCALE, HEIGHT * SCALE)
    assert _pixel(card, TILE_POINT) == color


def test_long_description_still_renders(tmp_path):
    card = CardRenderer().render(CatInTextResult("purrs " * 400, 1.0), tmp_path / "c.png")
    assert card.is_file()


def test_choice_tile_uses_class_colour(tmp_path):
    result = ChooseCatDogResult(str(CAT), "cat", 0.9, {"cat": 0.9, "dog": 0.1, "other": 0.0})
    card = CardRenderer().render(result, tmp_path / "c.png")
    assert _pixel(card, TILE_POINT) == "#2D55C8"


def test_image_and_score_cards_render(tmp_path):
    renderer = CardRenderer()
    image = renderer.render(CatInImageResult(str(CAT), 0.97), tmp_path / "out" / "image.png")
    score = renderer.render(ScoreCatDogResult(str(CAT), 0.1, 0.9, 0.9, 0.1, ""), tmp_path / "score.png")
    assert image.is_file() and score.is_file()


def test_crop_card_shows_the_crop(tmp_path):
    result = CropFaceResult(str(CAT), True, 0.95, 0.4, {}, str(CAT))
    assert CardRenderer().render(result, tmp_path / "c.png").is_file()


def test_face_not_found_has_a_card_and_other_errors_do_not(tmp_path):
    renderer = CardRenderer()
    missing = AppError("face_not_found", "No face.", image=str(CAT), face_probability=0.09)
    card = renderer.render_failure(missing, tmp_path / "c.png")
    assert _pixel(card, ((56 + 100) * SCALE, (ROW_TOP + 100) * SCALE)) == "#FBE9E9"
    assert renderer.render_failure(AppError("file_not_found", "Nope."), tmp_path / "d.png") is None
