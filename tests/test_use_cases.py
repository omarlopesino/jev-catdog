"""Use case tests with the fake gateway: the questions sent and the normalized results."""

from pathlib import Path

import pytest

from jev_catdog.errors import AppError
from jev_catdog.use_cases.choose_cat_dog import ChooseCatDog
from jev_catdog.use_cases.crop_animal_face import CropAnimalFace
from jev_catdog.use_cases.detect_cat_in_image import DetectCatInImage
from jev_catdog.use_cases.detect_cat_in_text import DetectCatInText
from jev_catdog.use_cases.score_cat_dog import ScoreCatDog
from conftest import FakeGateway, FakeLoader

BOX = {"type": "box", "box": {"top": 0.1, "bottom": 0.5, "left": 0.2, "right": 0.6}, "confidence": 0.7}


class FakeCropper:
    """Cropper that never writes to disk; it only remembers the box and returns the requested path."""

    def __init__(self):
        self.box = None

    def crop(self, source, box, destination):
        """Keeps the received box so it can be checked, and returns the destination untouched."""
        self.box = box
        return destination


def test_detect_cat_in_text_returns_probability():
    gateway = FakeGateway({"is_cat": {"type": "noul", "noul": 0.95}})
    result = DetectCatInText(gateway).execute("It meows and eats tuna")
    assert result.is_cat_probability == 0.95
    assert gateway.last_request.state == "It meows and eats tuna"


def test_detect_cat_in_image_attaches_photo(cat_image):
    gateway = FakeGateway({"is_cat": {"type": "noul", "noul": 0.9}})
    result = DetectCatInImage(gateway, FakeLoader()).execute(cat_image)
    assert result.is_cat_probability == 0.9
    assert list(gateway.last_request.images) == ["photo"]


def test_missing_image_is_file_not_found():
    gateway = FakeGateway({})
    with pytest.raises(AppError) as error:
        DetectCatInImage(gateway, FakeLoader()).execute(Path("nope.jpg"))
    assert error.value.code == "file_not_found"


def test_score_splits_probability_between_cat_and_dog(cat_image):
    answers = {"cat_to_dog": {"type": "score", "score": 0.1, "confidence": 0.9, "probabilities": {"0": 0.9, "1": 0.1}}}
    result = ScoreCatDog(FakeGateway(answers), FakeLoader()).execute(cat_image)
    assert (result.cat_probability, result.dog_probability) == (0.9, 0.1)
    assert "choice" in result.note


def test_choice_returns_option_and_probabilities(cat_image):
    probabilities = {"cat": 0.8, "dog": 0.15, "other": 0.05}
    answers = {"animal": {"type": "choice", "choice": "cat", "confidence": 0.8, "probabilities": probabilities}}
    result = ChooseCatDog(FakeGateway(answers), FakeLoader()).execute(cat_image)
    assert result.choice == "cat"
    assert result.probabilities == probabilities


def test_crop_face_saves_crop_when_face_is_found(cat_image, tmp_path):
    cropper = FakeCropper()
    gateway = FakeGateway({"has_face": {"type": "noul", "noul": 0.9}, "face": BOX})
    result = CropAnimalFace(gateway, FakeLoader(), cropper).execute(cat_image, tmp_path / "face.jpg")
    assert result.face_found and result.output == str(tmp_path / "face.jpg")
    assert result.box == {"top": 0.1, "bottom": 0.5, "left": 0.2, "right": 0.6}


def test_crop_face_fails_below_threshold(cat_image, tmp_path):
    cropper = FakeCropper()
    gateway = FakeGateway({"has_face": {"type": "noul", "noul": 0.1}, "face": BOX})
    with pytest.raises(AppError) as error:
        CropAnimalFace(gateway, FakeLoader(), cropper).execute(cat_image, tmp_path / "face.jpg")
    assert error.value.code == "face_not_found"
    assert cropper.box is None
