"""Fits images to Jev's limits before sending them: size per side and total pixels."""

import io
import math
from pathlib import Path

from PIL import Image

from jev_catdog.jev.request import ImageAsset

MAX_SIDE = 1568
MAX_PIXELS = 2_458_624
MIN_SIDE = 280


class ImagePreparer:
    """Loads an image, shrinks it if it exceeds TypeSafe's limits and encodes it as JPEG."""

    def prepare(self, path: Path) -> ImageAsset:
        """Returns the image ready to send, together with its original and sent sizes."""
        with Image.open(path) as image:
            image = image.convert("RGB")
            original = image.size
            scale = self._scale(original)
            if scale < 1:
                image = image.resize((round(original[0] * scale), round(original[1] * scale)))
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=90)
            return ImageAsset(buffer.getvalue(), path.name, original, image.size)

    @staticmethod
    def _scale(size: tuple[int, int]) -> float:
        """Smallest reduction factor that satisfies both the maximum side and the total pixel count."""
        width, height = size
        if min(width, height) < MIN_SIDE:
            raise ValueError(f"Image is {width}x{height}; Jev requires at least {MIN_SIDE} px per side.")
        by_side = MAX_SIDE / max(width, height)
        by_pixels = math.sqrt(MAX_PIXELS / (width * height))
        return min(1.0, by_side, by_pixels)
