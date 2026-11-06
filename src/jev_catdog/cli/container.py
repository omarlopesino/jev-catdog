"""Composition root: the only place that knows about the concrete implementations."""

from functools import cached_property

from jev_catdog.infrastructure.image_cropper import ImageCropper
from jev_catdog.infrastructure.image_preparer import ImagePreparer
from jev_catdog.infrastructure.settings import Settings
from jev_catdog.infrastructure.typesafe_gateway import TypeSafeGateway


class Container:
    """Builds the TypeSafe gateway, the image preparer and the image cropper on demand."""

    def __init__(self, dry_run: bool = False):
        self._dry_run = dry_run

    @cached_property
    def settings(self) -> Settings:
        """Environment configuration; dry-run mode needs no key because the API is never called."""
        return Settings.from_env(require_key=not self._dry_run)

    @cached_property
    def gateway(self) -> TypeSafeGateway:
        """HTTP gateway configured with the key, base URL and model from the environment."""
        return TypeSafeGateway(self.settings.api_key, self.settings.base_url, self.settings.model)

    @cached_property
    def loader(self) -> ImagePreparer:
        """Preparer that fits images within the size limits that Jev accepts for requests."""
        return ImagePreparer()

    @cached_property
    def cropper(self) -> ImageCropper:
        """Cropper that saves the box region taken from the original, full-resolution image."""
        return ImageCropper()
