"""Tests of the image preparer and cropper using temporary files generated with Pillow."""

from pathlib import Path

from PIL import Image

from jev_catdog.infrastructure.image_cropper import ImageCropper
from jev_catdog.infrastructure.image_preparer import MAX_SIDE, ImagePreparer
from jev_catdog.jev.answers import BoxAnswer


def _image(tmp_path: Path, size: tuple[int, int]) -> Path:
    """Creates a plain JPEG image of the given size in the test's temporary folder."""
    path = tmp_path / "img.jpg"
    Image.new("RGB", size, "orange").save(path)
    return path


def test_oversized_image_is_scaled_to_limits(tmp_path):
    asset = ImagePreparer().prepare(_image(tmp_path, (1280, 1933)))
    assert asset.original_size == (1280, 1933)
    assert max(asset.sent_size) == MAX_SIDE


def test_image_within_limits_is_not_resized(tmp_path):
    asset = ImagePreparer().prepare(_image(tmp_path, (1280, 853)))
    assert asset.sent_size == (1280, 853)


def test_crop_uses_fractions_of_original_size(tmp_path):
    source = _image(tmp_path, (1000, 500))
    box = BoxAnswer(top=0.2, bottom=0.6, left=0.1, right=0.5, confidence=0.9)
    output = ImageCropper().crop(source, box, tmp_path / "out" / "face.jpg")
    with Image.open(output) as cropped:
        assert cropped.size == (400, 200)
