"""Entry points of the five commands; each composes its use case and runs it."""

import argparse
from collections.abc import Callable
from pathlib import Path

from jev_catdog.cli.container import Container
from jev_catdog.cli.presenter import emit, fail
from jev_catdog.errors import AppError
from jev_catdog.use_cases.choose_cat_dog import ChooseCatDog
from jev_catdog.use_cases.crop_animal_face import DEFAULT_THRESHOLD, CropAnimalFace
from jev_catdog.use_cases.detect_cat_in_image import DetectCatInImage
from jev_catdog.use_cases.detect_cat_in_text import DetectCatInText
from jev_catdog.use_cases.score_cat_dog import ScoreCatDog

OUTPUT_DIR = Path("output")


def cat_detect_text() -> int:
    """cat-detect-text command: probability that a description refers to a cat."""
    parser = _parser("Probability (noul) that a description refers to a cat.")
    parser.add_argument("description", help="Natural-language description of the animal.")
    return _run(parser, lambda c: DetectCatInText(c.gateway), lambda args: (args.description,))


def cat_detect_image() -> int:
    """cat-detect-image command: probability that an image contains at least one cat."""
    parser = _image_parser("Probability (noul) that there is a cat in the image.")
    return _run(parser, lambda c: DetectCatInImage(c.gateway, c.loader), lambda args: (args.image,))


def score_cat_dog() -> int:
    """score-cat-dog command: places the image on an ordered scale from cat to dog."""
    parser = _image_parser("Cat-to-dog scale (score); a counterexample to choice.")
    return _run(parser, lambda c: ScoreCatDog(c.gateway, c.loader), lambda args: (args.image,))


def choice_cat_dog() -> int:
    """choice-cat-dog command: chooses whether the image shows a cat, a dog or something else."""
    parser = _image_parser("Chooses (choice) between cat, dog or something else.")
    return _run(parser, lambda c: ChooseCatDog(c.gateway, c.loader), lambda args: (args.image,))


def crop_cat_dog_face() -> int:
    """crop-cat-dog-face command: crops the animal's face or reports that it was not found."""
    parser = _image_parser("Crops (box) the face of the cat or dog in the image.")
    parser.add_argument("--out", type=Path, help="Path of the crop; defaults to output/<name>_face.jpg.")
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD, help="Minimum probability that a face is present."
    )
    return _run(
        parser,
        lambda c: CropAnimalFace(c.gateway, c.loader, c.cropper),
        lambda args: (args.image, args.out or OUTPUT_DIR / f"{args.image.stem}_face.jpg", args.threshold),
    )


def _parser(description: str) -> argparse.ArgumentParser:
    """Base parser with the shared options for inspecting the request sent to Jev."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_true", help="Include the request sent to Jev in the output.")
    parser.add_argument("--dry-run", action="store_true", help="Show the request without calling the API.")
    return parser


def _image_parser(description: str) -> argparse.ArgumentParser:
    """Base parser plus the positional argument with the path of the image to analyse."""
    parser = _parser(description)
    parser.add_argument("image", type=Path, help="Path of the image, e.g. ./data/cats/cats_01.jpg.")
    return parser


def _run(parser: argparse.ArgumentParser, build: Callable, inputs: Callable) -> int:
    """Composes the use case, runs it or shows its request, and presents the result as JSON."""
    args = parser.parse_args()
    container = Container(dry_run=args.dry_run)
    try:
        use_case = build(container)
        values = inputs(args)
        request = None
        if args.dry_run or args.verbose:
            request = use_case.request_for(values[0]).describe(container.settings.model)
        if args.dry_run:
            emit(request=request)
            return 0
        emit(use_case.execute(*values), request)
        return 0
    except AppError as error:
        return fail(error)
