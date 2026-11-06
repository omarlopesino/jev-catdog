"""Small ports the use cases rely on to load images and to save crops."""

from pathlib import Path
from typing import Protocol

from jev_catdog.errors import AppError
from jev_catdog.jev.answers import BoxAnswer
from jev_catdog.jev.request import ImageAsset


class ImageLoader(Protocol):
    """Loads an image from disk and keeps it within the limits that Jev accepts."""

    def prepare(self, path: Path) -> ImageAsset:
        """Reads the given image and returns it encoded and fitted to Jev's limits."""
        ...


class Cropper(Protocol):
    """Crops an image using a Jev box and returns the path of the created file."""

    def crop(self, source: Path, box: BoxAnswer, destination: Path) -> Path:
        """Saves the box region of the original image to destination and returns that path."""
        ...


def load_image(loader: ImageLoader, path: Path) -> ImageAsset:
    """Loads the image, turning a missing file or an invalid image into normalized errors."""
    if not path.is_file():
        raise AppError("file_not_found", f"File not found: {path}.", image=str(path))
    try:
        return loader.prepare(path)
    except (OSError, ValueError) as error:
        raise AppError("invalid_image", str(error), image=str(path)) from error
