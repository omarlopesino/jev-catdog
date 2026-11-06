"""Crops the original image using a Jev box expressed as fractions of its size."""

from pathlib import Path

from PIL import Image

from jev_catdog.jev.answers import BoxAnswer


class ImageCropper:
    """Saves the crop of the box from the original image, at full resolution."""

    def crop(self, source: Path, box: BoxAnswer, destination: Path) -> Path:
        """Converts fractions to pixels, crops, creates the destination folder and saves the JPEG."""
        with Image.open(source) as image:
            width, height = image.size
            region = (
                round(box.left * width),
                round(box.top * height),
                round(box.right * width),
                round(box.bottom * height),
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            image.convert("RGB").crop(region).save(destination, format="JPEG", quality=95)
        return destination
