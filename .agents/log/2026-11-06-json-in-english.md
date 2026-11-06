# 2026-11-06: JSON text in English

## What was done

- Every piece of text that ends up in the JSON output is now in English:
  - the error `message` for `file_not_found`, `invalid_image`, `missing_api_key`, `api_unreachable`, `api_error`, `refusal` and `face_not_found`;
  - the `note` of `score-cat-dog`.
- Files: `use_cases/ports.py`, `use_cases/crop_animal_face.py`, `use_cases/score_cat_dog.py`, `infrastructure/settings.py`, `infrastructure/typesafe_gateway.py`, `infrastructure/image_preparer.py` and `jev/answers.py`.
- New convention in `CLAUDE.md`: JSON text is in English.

## Decisions and why

- The user will use the output in an English article. The keys were already in English, so now the whole JSON is consistent.
- The argparse help (`--help`) and the docstrings stay in Spanish: they are not part of the JSON and this change did not cover them.

## Verification

- `uv run pytest`: 18 pass.
- `uv run crop-cat-dog-face nope.jpg` returns `"message": "File not found: nope.jpg."`.
- Search for strings with accents or ñ in `src/`: only argparse help text and docstrings remain.
